"""Consistency of the bilingual reports, result tables and public links."""
import json
from pathlib import Path
import re
import unittest
import hashlib
import ast
import operator
import zipfile
from collections import Counter

ROOT = Path(__file__).resolve().parents[1]


def report_projects():
    return [(language, ROOT / 'reports' / (language + suffix))
            for suffix in ('', '_full') for language in ('en', 'zh')
            if (ROOT / 'reports' / (language + suffix) / 'main.tex').is_file()]


class Documents(unittest.TestCase):
    def test_dimensional_research_accounts_and_navigation(self):
        rows = json.loads((ROOT / 'constructions/catalog/results.json').read_text())['results']
        expected = {r['dimension']: r['lower_bound'] for r in rows}
        for suffix in (".md", ".zh-CN.md"):
            index = (ROOT / "research" / ("README" + suffix)).read_text()
            homepage = (ROOT / ("README" + suffix)).read_text()
            paths = {path.name for path in (ROOT / "research/dimensions").glob("*" + suffix)
                     if suffix != ".md" or not path.name.endswith(".zh-CN.md")}
            self.assertEqual(paths, {str(d) + suffix for d in expected})
            for dimension, bound in expected.items():
                relative = f"dimensions/{dimension}{suffix}"
                text = (ROOT / "research" / relative).read_text()
                self.assertIn(f"]({relative})", index)
                self.assertIn(f"](research/{relative})", homepage)
                self.assertIn(r"\boxed{" + str(bound) + "}", text)
                self.assertIn("../../constructions/", text)
                other = ".zh-CN.md" if suffix == ".md" else ".md"
                self.assertIn(f"]({dimension}{other})", text)

    def test_shared_blocker_counts_in_the_research_accounts(self):
        root = ROOT / "constructions/codes"
        entries = json.loads((root / "data/exchanges/exchanges.json").read_text())["exchanges"]
        expected = {33: (10, 9, 20, {1: 1, 2: 8, 3: 1}),
                    34: (7, 6, 9, {1: 6, 3: 1}),
                    37: (40, 37, 84, {1: 8, 2: 22, 3: 8, 4: 2}),
                    39: (15, 14, 30, {1: 1, 2: 13, 3: 1})}
        for entry in entries:
            if entry["dimension"] not in expected:
                continue
            parent = [int(line, 16) for line in (root / entry["parent"]).read_text().splitlines()
                      if line.strip() and not line.startswith(("#", "$"))]
            additions = [int(value, 16) for value in entry["added_hex"]]
            blockers = [{a for a in parent if (a & b).bit_count() > 4} for b in additions]
            union = set().union(*blockers)
            actual = (len(additions), len(union), sum(map(len, blockers)),
                      dict(Counter(map(len, blockers))))
            self.assertEqual(actual, expected[entry["dimension"]])
            self.assertEqual(union, {int(value, 16) for value in entry["removed_hex"]})
            if entry["dimension"] == 33:
                self.assertEqual(max(Counter(a for group in blockers for a in group).values()), 4)

    def test_saved_search_distinguishes_relaxation_from_construction(self):
        record = json.loads((ROOT / "research/data/d34-exchange-search.json").read_text())
        self.assertEqual(record["dimension"], 34)
        for key in ("parent", "exchange"):
            self.assertTrue((ROOT / record[key]).is_file())
        first, final = record["iterations"]
        self.assertFalse(first["internally_compatible"])
        self.assertEqual(first["new_packing_constraints"], first["repeated_five_subset_keys"])
        self.assertTrue(final["internally_compatible"])
        self.assertEqual(final["repeated_five_subset_keys"], 0)
        for iteration in record["iterations"]:
            self.assertEqual(iteration["selected_candidates"] - iteration["deleted_old_supports"],
                             iteration["objective"])
        self.assertEqual(record["parent_size"] + final["objective"], record["final_size"])
        exchange = next(row for row in json.loads((ROOT / record["exchange"]).read_text())["exchanges"]
                        if row["dimension"] == 34)
        self.assertEqual(len(exchange["added_hex"]), final["selected_candidates"])
        self.assertEqual(len(exchange["removed_hex"]), final["deleted_old_supports"])

    def test_livestream_citation_uses_original_article(self):
        source = "https://hznews.hangzhou.com.cn/kejiao/content/2026-09/23/content_9314105.htm"
        for name in ("README.md", "README.zh-CN.md", "research/livestream.md"):
            self.assertIn(source, (ROOT / name).read_text(), name)

    def test_report_tables_match_catalogue(self):
        catalog = json.loads((ROOT / "constructions/catalog/results.json").read_text())
        expected = [(r["dimension"], r["lower_bound"], r["comparison"]["lower_bound"],
                     r["comparison"]["gain"]) for r in catalog["results"]]
        self.assertEqual(catalog["result_count"], len(expected))
        for language, report in report_projects():
            text = (report / "sections/results.tex").read_text()
            rows = re.findall(r"^(\d+) & (\d+) & (\d+) & (\d+) & \\cite\{[^}]+\} \\\\", text, re.M)
            scope = (report / 'latex/collection.tex').read_text()
            count = int(re.search(r'\\ResultCount\}\{(\d+)\}', scope)[1])
            if report.name.endswith('_full'):
                selected = expected
            else:
                with zipfile.ZipFile(report / 'certificates.zip') as archive:
                    frozen = json.loads(archive.read('constructions/catalog/results.json'))
                selected = [(r['dimension'], r['lower_bound'],
                             r['comparison']['lower_bound'], r['comparison']['gain'])
                            for r in frozen['results']]
            self.assertEqual(count, len(selected))
            self.assertEqual([tuple(map(int, row)) for row in rows], selected)
        for filename in ("README.md", "README.zh-CN.md", "research/results.md"):
            rows = re.findall(r"^\| (\d+) \| ([\d,]+) \| ([\d,]+) \| \+([\d,]+) \|$",
                              (ROOT / filename).read_text(), re.M)
            self.assertEqual([tuple(int(n.replace(",", "")) for n in row) for row in rows], expected)
        for _, bound, comparator, gain in expected:
            self.assertEqual(bound - comparator, gain)

    def test_bilingual_structure_matches(self):
        for suffix in ('', '_full'):
            en_dir = ROOT / 'reports' / ('en' + suffix)
            zh_dir = ROOT / 'reports' / ('zh' + suffix)
            for relative in ("sections/constructions.tex", "latex/collection.tex", "refs.bib"):
                self.assertEqual((en_dir / relative).read_bytes(),
                                 (zh_dir / relative).read_bytes(), relative)
            en = (en_dir / 'main.tex').read_text()
            zh = (zh_dir / 'main.tex').read_text()
            self.assertEqual(re.findall(r"\\input\{([^}]+)\}", en),
                             re.findall(r"\\input\{([^}]+)\}", zh))
        for language, report in report_projects():
            for path in report.rglob("*.tex"):
                for target in re.findall(r"\\input\{([^}]+)\}", path.read_text()):
                    self.assertTrue((report / (target + ".tex")).is_file(), str(path) + ":" + target)

    def test_citations_have_bibliography_entries(self):
        for language, report in report_projects():
            keys = set(re.findall(r"@\w+\{([^,]+),", (report / "refs.bib").read_text()))
            for path in report.rglob("*.tex"):
                for group in re.findall(r"\\cite(?:\[[^\]]*\])?\{([^}]+)\}", path.read_text()):
                    self.assertLessEqual(set(group.split(",")), keys, str(path))

    def test_paper_table_when_present(self):
        paper = ROOT / "paper/sections/introduction.tex"
        if not paper.is_file():
            self.skipTest("This collection contains reports and construction data")
        catalog = json.loads((ROOT / "constructions/catalog/results.json").read_text())
        expected = [(r["dimension"], r["lower_bound"]) for r in catalog["results"]]
        rows = re.findall(r"^(\d+)&(\d+)&", paper.read_text(), re.M)
        self.assertEqual([(int(d), int(n)) for d, n in rows], expected)
        comparisons = re.findall(r"^(\d+)&(\d+)&(\d+)&(\d+)&", paper.read_text(), re.M)
        self.assertEqual([tuple(map(int, row)) for row in comparisons], [
            (r['dimension'], r['lower_bound'], r['comparison']['lower_bound'],
             r['comparison']['gain']) for r in catalog['results']])

    def test_paper_lattice_models_and_structure_theorem(self):
        base = ROOT / 'paper/sections'
        lifting = (base / 'p48.tex').read_text()
        section = (base / 'sections.tex').read_text()
        neighbour = (base / 'pless-neighbour.tex').read_text()
        self.assertIn(r'Section~\ref{sec:qr-neighbour}', lifting)
        self.assertNotIn('identifies the neighbour used', neighbour)
        self.assertIn(r'\label{d43:thm:structure}', section)
        self.assertIn('Let $L$ be an extremal even unimodular lattice of rank 48', section)
        self.assertIn(r'\iota:\sqrt3E_8\hookrightarrow L', section)
        self.assertIn(r'Precomposing $\iota$', section)
        self.assertIn(r'\begin{corollary}\label{d43:thm:main}', section)

    def test_paper_inputs_references_and_current_scope(self):
        base = ROOT / 'paper'
        seen = set()
        def read_project(name):
            if name in seen:
                return ''
            seen.add(name)
            path = base / (name + '.tex')
            self.assertTrue(path.is_file(), str(path))
            text = path.read_text()
            return text + '\n' + '\n'.join(
                read_project(target) for target in re.findall(r'\\input\{([^}]+)\}', text))
        text = read_project('main')
        self.assertIn('sections/pless-neighbour', seen)
        self.assertNotIn('sections/parity', seen)
        main = (base / 'main.tex').read_text()
        self.assertIn('nineteen dimensions', main)
        self.assertNotIn('dimension 18', text)
        labels = re.findall(r'\\label\{([^}]+)\}', text)
        self.assertEqual(len(labels), len(set(labels)))
        references = set(re.findall(r'\\(?:ref|eqref)\{([^}]+)\}', text))
        self.assertLessEqual(references, set(labels))
        keys = set(re.findall(r'@\w+\{([^,]+),', (base / 'references.bib').read_text()))
        for group in re.findall(r'\\cite(?:\[[^\]]*\])?\{([^}]+)\}', text):
            self.assertLessEqual(set(group.split(',')), keys)

    def test_p48_paper_gain_table_matches_finite_unions(self):
        data = json.loads((ROOT / 'research/data/p48-search.json').read_text())['families']
        catalogue = json.loads((ROOT / 'constructions/catalog/results.json').read_text())['results']
        total = {r['dimension']: r['comparison']['gain'] for r in catalogue}
        text = (ROOT / 'paper/sections/p48.tex').read_text()
        table = text.split(r'\label{tab:p48-gain}', 1)[1]
        rows = re.findall(r'^(\d+)&(\d+)&(\d+)&(\d+)&(\d+)\\\\', table, re.M)
        self.assertEqual(len(rows), 7)
        for d, old_union, class_gain, image_gain, gain in rows:
            d, old_union, class_gain, image_gain, gain = map(int, (d, old_union, class_gain, image_gain, gain))
            record = data[str(d)]
            self.assertEqual(old_union, record['same_family_original_class_union'])
            self.assertEqual(class_gain, 2 * (record['union'] - old_union))
            self.assertEqual(class_gain + image_gain, gain)
            self.assertEqual(gain, total[d])

    def test_relative_document_links(self):
        paths = [ROOT / "README.md", ROOT / "README.zh-CN.md", ROOT / "RIGHTS.md"]
        for name in ("reports", "research", "evidence", "reproducibility", "constructions", "paper"):
            if (ROOT / name).exists():
                paths += list((ROOT / name).rglob("*.md"))
        for path in paths:
            for target in re.findall(r"\]\(([^\s)]+)\)", path.read_text()):
                if ":" in target or target.startswith("#"):
                    continue
                linked = path.parent / target.split("#")[0]
                if linked.suffix == ".pdf":
                    self.assertTrue(linked.with_suffix(".tex").is_file(), str(linked))
                else:
                    self.assertTrue(linked.exists(), str(linked))

    def test_report_front_matter_and_sources(self):
        for language, report in report_projects():
            main = (report / "main.tex").read_text()
            self.assertIn(r"\input{latex/authors}", main)
            self.assertIn(r"\input{sections/abstract}", main)
            self.assertIn(r"\tableofcontents", main)
            authors = (report / "latex/authors.tex").read_text()
            self.assertIn("hansomchen@zju.edu.cn", authors)
            self.assertIn("yangyihao@zju.edu.cn", authors)
            self.assertTrue((report / "figures/qiushi-engine-logo.png").is_file())
        self.assertIn("接吻数新下界的自主发现", (ROOT / "reports/zh/main.tex").read_text())
        self.assertIn("Autonomous Discovery of New Lower Bounds", (ROOT / "reports/en/main.tex").read_text())
        self.assertIn("编码构造、格提升与截面计数", (ROOT / "reports/zh/main.tex").read_text())

    def test_report_date_and_author_order(self):
        expected = ("Shuxing Yang, Rui Zhao, Junyao Wu, Yize Wang, Fujia Chen, Kaihao Zhu, "
                    "Wenhao Li, Zichen Li, Yaqi Li, Shenzhan Hong, Yuang Pan, Junjie Yang, "
                    "Taowen Deng, Jincheng Mi, Hongsheng Chen, Yihao Yang")
        for language, report in report_projects():
            text = (report / "latex/authors.tex").read_text()
            self.assertIn(r"\newcommand{\ReportAuthorNames}{" + expected + "}", text)
            main = (report / "main.tex").read_text()
            date = '25 September 2026' if language == 'en' else '2026年9月25日'
            self.assertIn(r'\date{' + date + '}', main)
        cff = (ROOT / "CITATION.cff").read_text()
        names = re.findall(r"  - family-names: (.+)\n    given-names: (.+)", cff)
        self.assertEqual(", ".join(given + " " + family for family, given in names), expected)

    def test_paper_pdf_and_date(self):
        main = (ROOT / 'paper/main.tex').read_text()
        self.assertIn(r'\date{25 September 2026}', main)
        self.assertTrue((ROOT / 'paper/main.pdf').read_bytes().startswith(b'%PDF-'))
        self.assertIn('!paper/main.pdf', (ROOT / '.gitignore').read_text().splitlines())
        for name in ('README.md', 'README.zh-CN.md'):
            self.assertIn('(paper/main.pdf)', (ROOT / name).read_text())
        self.assertIn('(main.pdf)', (ROOT / 'paper/README.md').read_text())

    def test_paper_authors_match_the_citation_record(self):
        source = (ROOT / 'paper/authors.tex').read_text()
        authors = re.findall(r'\\author(?:\[[^\]]*\])?\{([A-Za-z ]+)', source)
        cff = (ROOT / 'CITATION.cff').read_text()
        names = re.findall(r'  - family-names: (.+)\n    given-names: (.+)', cff)
        self.assertEqual(authors, [given + ' ' + family for family, given in names])
        for name in ('Hongsheng Chen', 'Yihao Yang'):
            self.assertIn(r'\author[]{' + name + r'\textsuperscript{*}}', source)
        self.assertIn(r'\hypersetup{pdfauthor={\AuthorNames}}', source)

    def test_complete_affiliations_have_the_established_order(self):
        english = ('College of Information Science and Electronic Engineering, '
                   'Zhejiang University', 'Qiushi Engine Team')
        chinese = ('浙江大学信息与电子工程学院', '求是引擎团队')
        for relative, macro, expected in (
                ('paper/authors.tex', 'PaperAffiliation', english),
                ('reports/en_full/latex/authors.tex', 'ReportAffiliation', english),
                ('reports/zh_full/latex/authors.tex', 'ReportAffiliation', chinese)):
            source = (ROOT / relative).read_text()
            content = source.split('\\newcommand{\\' + macro + '}{', 1)[1].split('}', 1)[0]
            self.assertEqual(tuple(part.strip() for part in content.split(r'\\')), expected)
        preamble = (ROOT / 'paper/preamble.tex').read_text()
        self.assertIn(r'\AddToHook{cmd/@setauthors/after}', preamble)
        self.assertIn(r'\PaperAffiliation\par', preamble)

    def test_paper_title_page_has_one_correspondence_block(self):
        authors = (ROOT / 'paper/authors.tex').read_text()
        preamble = (ROOT / 'paper/preamble.tex').read_text()
        self.assertNotIn(r'\thanks{', authors)
        self.assertNotIn('Hangzhou, China', authors)
        self.assertEqual(authors.count('Corresponding authors:'), 1)
        correspondence = authors.split(r'\newcommand{\PaperCorrespondence}{', 1)[1].split(
            r'\hypersetup', 1)[0]
        self.assertNotIn(r'\\', correspondence)
        self.assertIn(r'\PaperCorrespondence\par', preamble)
        self.assertLess(preamble.index(r'\PaperAffiliation\par'),
                        preamble.index(r'\PaperCorrespondence\par'))
        block = authors.split(r'\newcommand{\PaperAuthorBlock}{%', 1)[1].split(
            r'\newcommand{\PaperAffiliation}', 1)[0]
        names = re.findall(r'\\author(?:\[[^\]]*\])?\{([A-Za-z ]+)', authors)
        display_names = re.findall(r'[A-Z][a-z]+~[A-Z][a-z]+', block)
        self.assertEqual([name.replace('~', ' ') for name in display_names], names)
        self.assertEqual(block.count(r'\\'), 2)

    def test_dense_code_usage_includes_all_six_ambient_dimensions(self):
        codes = (ROOT / 'paper/sections/codes.tex').read_text()
        appendix = (ROOT / 'paper/sections/code-tables.tex').read_text()
        self.assertIn(r'32&17&8&1&8&131072&32--37\\', codes)
        self.assertIn(r'used unchanged in ambient dimensions $32$--$37$', appendix)
        data = ROOT / 'constructions/codes'
        rows = json.loads((data / 'hadamard/data/top_code.json').read_text())['generator_matrix']
        masks = [sum(bit << i for i, bit in enumerate(row)) for row in rows]
        for dimension in (33, 34, 37):
            kernel = (data / f'data/d{dimension}_kernel.txt').read_text()
            self.assertEqual(masks, [int(row, 16) for row in kernel.splitlines() if row.strip()])

    def test_paper_title_and_research_attribution(self):
        title = 'Large-Scale Autonomous Discovery of Kissing Number Constructions'
        main = (ROOT / 'paper/main.tex').read_text()
        preamble = (ROOT / 'paper/preamble.tex').read_text()
        self.assertIn(r'\title[Autonomous discovery of kissing constructions]{' + title + '}', main)
        self.assertIn(r'\renewcommand{\@settitle}', preamble)
        self.assertIn(r'\normalfont\fontsize{13}{16}\selectfont\bfseries\@title', preamble)
        self.assertNotIn(r'\uppercasenonmath\@title', preamble)
        self.assertIn('pdftitle={' + title + '}', preamble)
        for name in ('paper/README.md', 'README.md', 'README.zh-CN.md', 'reports/README.md'):
            self.assertIn(title, (ROOT / name).read_text(), name)
        abstract = main.split(r'\begin{abstract}', 1)[1].split(r'\end{abstract}', 1)[0]
        self.assertLessEqual(len(abstract.split()), 200)
        self.assertIn('nineteen dimensions', abstract)
        self.assertIn('Qiushi Engine', (ROOT / 'paper/sections/introduction.tex').read_text())
        self.assertIn(r'\label{sec:autonomous-research}',
                      (ROOT / 'paper/sections/verification.tex').read_text())

    def test_complete_openings_and_mathematical_scope(self):
        paper = (ROOT / 'paper/main.tex').read_text()
        english = (ROOT / 'reports/en_full/sections/abstract.tex').read_text()
        paper_abstract = paper.split(r'\begin{abstract}', 1)[1].split(r'\end{abstract}', 1)[0]
        report_abstract = english.split(r'\begin{abstract}', 1)[1].split(r'\par\smallskip', 1)[0]
        self.assertEqual(paper_abstract.strip(), report_abstract.strip())
        for path in ('paper/sections/introduction.tex',
                     'reports/en_full/sections/introduction.tex'):
            text = (ROOT / path).read_text()
            self.assertIn('with the first layer fixed', text)
            self.assertIn('In dimensions 32--37 and 39', text)
            self.assertIn('rigorous interval', text)
            for key in ('alphaevolve', 'packingstar-discovery', 'einsteinarena',
                        'station', 'qiushi-optics', 'johansson-arb'):
                self.assertIn(r'\cite{' + key + '}', text)
        for language in ('en_full', 'zh_full'):
            main = (ROOT / f'reports/{language}/main.tex').read_text()
            self.assertNotIn('Structural Constructions for Kissing Numbers', main)
            section = (ROOT / f'reports/{language}/sections/sections.tex').read_text()
            self.assertIn(r'|X_L\cap U_L^\perp|=2553792', section)
            self.assertIn(r'W(E_8)', section)

    def test_related_work_versions_remain_distinct(self):
        for path in ('paper/references.bib', 'reports/en_full/refs.bib',
                     'reports/zh_full/refs.bib'):
            bib = (ROOT / path).read_text()
            self.assertIn('https://arxiv.org/abs/2511.13391v4', bib)
            self.assertIn('https://arxiv.org/abs/2511.13391v5', bib)
            old = bib.split('@misc{packingstar,', 1)[1].split('@misc{', 1)[0]
            new = bib.split('@misc{packingstar-discovery,', 1)[1].split('@misc{', 1)[0]
            self.assertIn('and Bo Li', old)
            self.assertNotIn('and Bo Li', new)
            for entry, version in ((old, 'v4'), (new, 'v5')):
                self.assertIn('year={2026}', entry)
                self.assertIn('{arXiv:2511.13391' + version + '}', entry)

    def test_current_dimension32_comparison_uses_the_updated_code_table(self):
        catalog = json.loads((ROOT / 'constructions/catalog/results.json').read_text())
        row = next(r for r in catalog['results'] if r['dimension'] == 32)
        sources = json.loads((ROOT / 'constructions/catalog/comparison-sources.json').read_text())
        source = next(s for s in sources['sources'] if s['id'] == row['comparison']['source_id'])
        parameters = source['code_parameters']
        self.assertEqual(parameters, {'length': 32, 'distance': 8, 'weight': 8, 'size': 1671})
        bound = 2**17 + 128 * parameters['size'] + 2 * 32 * 31
        self.assertEqual(bound, source['derived_lower_bound'])
        self.assertEqual(bound, row['comparison']['lower_bound'])
        self.assertEqual(row['lower_bound'] - bound, 640)
        self.assertEqual(row['comparison']['retrieved_date'], source['retrieved_date'])
        self.assertEqual(source['retrieved_date'], '2026-09-27')
        for name in ('research/dimensions/32.md', 'research/dimensions/32.zh-CN.md'):
            text = (ROOT / name).read_text().replace(',', '')
            for value in ('1667', '1671', '1676', '346944', '640', '1152'):
                self.assertIn(value, text)

    def test_corrected_reference_metadata_agrees_across_editions(self):
        paths = ('paper/references.bib', 'reports/en_full/refs.bib',
                 'reports/zh_full/refs.bib')
        bibliographies = [{key: entry.strip() for entry, key in re.findall(
            r'(@\w+\{([^,]+),[\s\S]*?)(?=\n@|\Z)', (ROOT / name).read_text())}
            for name in paths]
        keys = ('packingstar', 'packingstar-data', 'brouwer', 'echols', 'antipode',
                'dorofeev', 'qiushi-optics', 'latticecatalogue', 'nebe-designs',
                'crosssections', 'takhanov-yun', 'kissingnumbers', 'lindow27',
                'p48p-catalogue', 'signed-johnson')
        for key in keys:
            self.assertEqual(bibliographies[0][key], bibliographies[1][key], key)
            self.assertEqual(bibliographies[1][key], bibliographies[2][key], key)
        for bib in bibliographies:
            self.assertIn('author={Alexey Kravatskiy}', bib['kissingnumbers'])
            self.assertIn('dimensions 18 through 96, with verification packages',
                          bib['kissingnumbers'])
            self.assertIn('cf14c5ef4db6059bbf2e570e3f0ce24edfda243e', bib['kissingnumbers'])
            self.assertIn('GitHub pull request', bib['lindow27'])
            self.assertIn('@incollection{nebe-designs,', bib['nebe-designs'])
            self.assertIn('year={2013}', bib['nebe-designs'])
            self.assertIn('10.1090/conm/587/11672', bib['nebe-designs'])

    def test_cited_preprints_display_their_fixed_versions(self):
        versions = {'alphaevolve': '2506.13131v1',
                    'packingstar-discovery': '2511.13391v5',
                    'einsteinarena': '2606.10402v2', 'station': '2608.23691v2',
                    'qiushi-optics': '2604.27092v1', 'packingstar': '2511.13391v4',
                    'echols': '2608.13906v1', 'takhanov-yun': '2609.21591v2',
                    'signed-johnson': '2606.03299v1', 'dorofeev': '2607.20359v4'}
        for name in ('paper/references.bib', 'reports/en_full/refs.bib',
                     'reports/zh_full/refs.bib'):
            text = (ROOT / name).read_text()
            for key, version in versions.items():
                entry = text.split('@misc{' + key + ',', 1)[1].split('\n@', 1)[0]
                self.assertIn(r'\href{https://arxiv.org/abs/' + version +
                              '}{arXiv:' + version + '}', entry)

    def test_complete_report_equatorial_proof_ends_with_its_formula(self):
        source = (ROOT / 'reports/zh_full/sections/equatorial.tex').read_text()
        self.assertIn(r'K(38)\ge591612+2\cdot144=591900.\qedhere', source)

    def test_section_statistic_is_explained_at_its_first_display(self):
        source = (ROOT / 'paper/sections/introduction.tex').read_text()
        explanation = source.index(r'let $f(y)$ count')
        inequality = source.index(r'f(e_1)+f(e_2)+f(e_3)')
        self.assertLess(explanation, inequality)
        self.assertIn('inner-product signature', source[explanation:inequality])
        self.assertIn(r'\ref{sec:projection45}', source[explanation:inequality])

    def test_leech_checkers_are_identified_in_verification_section(self):
        source = (ROOT / 'paper/sections/verification.tex').read_text()
        for name in ('leech/verify.py', 'leech/verify_independent.py'):
            self.assertIn(r'\qpath{' + name + '}', source)
            self.assertTrue((ROOT / 'constructions' / name).is_file())

    def test_complete_report_replay_recipe_includes_interval_dependency(self):
        for language in ('en_full', 'zh_full'):
            source = (ROOT / f'reports/{language}/sections/finite-data.tex').read_text()
            recipe = source.rsplit('\n\n', 1)[1]
            for dependency in ('SageMath', 'NumPy', 'SymPy', 'python-flint', 'C++'):
                self.assertIn(dependency, recipe)
            self.assertIn('python3 tools/reproduce.py --suite all', recipe)

    def test_short_image_table_cannot_split_across_pages(self):
        source = (ROOT / 'reports/zh_full/sections/p48.tex').read_text()
        self.assertNotIn(r'\begin{longtable}', source)
        table = source.split(r'\begin{table}', 1)[1].split(r'\end{table}', 1)[0]
        for k in range(1, 8):
            self.assertRegex(table, rf'(?m)^{k} & ')

    def test_undated_catalogues_have_no_invented_publication_year(self):
        for name in ('paper/references.bib', 'reports/en_full/refs.bib',
                     'reports/zh_full/refs.bib'):
            text = (ROOT / name).read_text()
            for key in ('latticecatalogue', 'p48p-catalogue'):
                entry = text.split('@misc{' + key + ',', 1)[1].split('\n@', 1)[0]
                self.assertIn('year={undated}', entry)
                self.assertIn('Last modified 18 July 2014', entry)
                self.assertIn('accessed 27 September 2026', entry)

    def test_bibliographies_use_first_citation_order(self):
        self.assertIn(r'\bibliographystyle{unsrturl}',
                      (ROOT / 'paper/main.tex').read_text())
        self.assertIn(r'\usepackage{cite}',
                      (ROOT / 'paper/preamble.tex').read_text())
        for language in ('en_full', 'zh_full'):
            self.assertIn(r'\bibliographystyle{unsrtnat}',
                          (ROOT / f'reports/{language}/main.tex').read_text())
        for path in ('paper/sections/introduction.tex',
                     'reports/en_full/sections/introduction.tex',
                     'reports/zh_full/sections/introduction.tex'):
            first = re.search(r'\\cite(?:\[[^\]]*\])?\{([^}]+)\}',
                              (ROOT / path).read_text())
            self.assertEqual(first[1], 'musin')

    def test_doi_breaks_preserve_identifiers(self):
        breaks = r'\def\UrlBreaks{\do\/\do\-}\def\UrlBigBreaks{}'
        self.assertIn(r'\DeclareUrlCommand\path{\urlstyle{tt}' + breaks + '}',
                      (ROOT / 'paper/preamble.tex').read_text())
        for language in ('en_full', 'zh_full'):
            text = (ROOT / f'reports/{language}/latex/preamble.tex').read_text()
            self.assertIn(r'\DeclareUrlCommand\doiurl{\urlstyle{rm}' + breaks + '}', text)
            self.assertIn(r'\href{https://doi.org/#1}{\doiurl{#1}}', text)

    def test_mathematical_inputs_are_present(self):
        catalog = json.loads((ROOT / "constructions/catalog/results.json").read_text())
        for row in catalog["results"]:
            for relative in row["artifact_ids"]:
                self.assertTrue((ROOT / relative).is_file(), relative)

    def test_artifact_identities(self):
        catalogue = json.loads((ROOT / "constructions/catalog/artifacts.json").read_text())
        for entry in catalogue["artifacts"]:
            path = ROOT / entry["path"]
            self.assertEqual(path.stat().st_size, entry["bytes"], entry["path"])
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), entry["sha256"], entry["path"])

    def test_count_formulas_and_proof_map(self):
        operations = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul}
        def integer_expression(node):
            if isinstance(node, ast.Constant) and type(node.value) is int:
                return node.value
            if isinstance(node, ast.BinOp) and type(node.op) in operations:
                return operations[type(node.op)](integer_expression(node.left), integer_expression(node.right))
            raise ValueError("Expected an integer sum or product")
        catalogue = json.loads((ROOT / "constructions/catalog/results.json").read_text())
        proof = (ROOT / "evidence/proof-map.md").read_text()
        dimensions = [r["dimension"] for r in catalogue["results"]]
        self.assertEqual([int(d) for d in re.findall(r"^### Dimension (\d+)$", proof, re.M)], dimensions)
        for row in catalogue["results"]:
            value = integer_expression(ast.parse(row["count_formula"], mode="eval").body)
            self.assertEqual(value, row["lower_bound"])
            self.assertIn(row["count_formula"], proof)

    def test_source_copy_identities(self):
        for manifest in ROOT.glob("constructions/**/source-manifest.json"):
            for entry in json.loads(manifest.read_text())["files"]:
                path = manifest.parent / entry["path"]
                self.assertTrue(path.is_file(), str(path))
                self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), entry["sha256"], str(path))


if __name__ == "__main__":
    unittest.main()
