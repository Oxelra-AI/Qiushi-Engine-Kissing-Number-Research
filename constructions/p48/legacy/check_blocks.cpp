// Exact finite-input checker. It does NOT prove the ambient minimum or priority.
#include <array>
#include <algorithm>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <map>
#include <sstream>
#include <stdexcept>
#include <string>
#include <unordered_set>
#include <vector>
using Row = std::array<int16_t,48>;
int mod(int64_t x, int p) { return int((x%p+p)%p); }
int S[24][24];
std::array<int64_t,48> chi{}, glue{};
void model() {
    for(int j=1;j<24;++j) { S[0][j]=1; S[j][0]=-1; }
    for(int i=1;i<24;++i) for(int j=1;j<24;++j) if(i!=j) {
        int a=mod(i-j,23), r=1;
        for(int k=0;k<11;++k) r=r*a%23;
        S[i][j]=(r==1?1:-1);
    }
    for(int i=0;i<24;++i) for(int j=0;j<24;++j) {
        int d=0; for(int k=0;k<24;++k) d+=S[i][k]*S[j][k];
        if(d!=(i==j?23:0)) throw std::runtime_error("Paley orthogonality");
    }
    int B[48][48]={};
    for(int i=0;i<24;++i) {
        B[i][i]=1;
        for(int j=0;j<24;++j) B[i][24+j]=S[i][j];
        B[24+i][24+i]=3;
    }
    int G[48][48]={}, a[48][49]={};
    for(int i=0;i<48;++i) for(int j=0;j<48;++j) {
        int d=0; for(int k=0;k<48;++k) d+=B[i][k]*B[j][k];
        if(d%3) throw std::runtime_error("nonintegral Gram");
        G[i][j]=d/3; a[i][j]=mod(G[i][j],2);
    }
    for(int i=0;i<48;++i) a[i][48]=mod(G[i][i],2);
    int rank=0; std::array<int,48> where; where.fill(-1);
    for(int c=0;c<48;++c) {
        int r=rank; while(r<48&&!a[r][c]) ++r;
        if(r==48) continue;
        for(int j=0;j<49;++j) std::swap(a[r][j],a[rank][j]);
        for(int i=0;i<48;++i) if(i!=rank&&a[i][c])
            for(int j=0;j<49;++j) a[i][j]^=a[rank][j];
        where[c]=rank++;
    }
    int coeff[48]={};
    for(int c=0;c<48;++c) if(where[c]>=0) coeff[c]=a[where[c]][48];
    for(int j=0;j<48;++j) for(int i=0;i<48;++i) chi[j]+=int64_t(coeff[i])*B[i][j];
    glue=chi; glue[0]+=6;
    for(int i=0;i<48;++i) {
        int64_t d=0; for(int j=0;j<48;++j) d+=B[i][j]*chi[j];
        if(d%3||mod(d/3-G[i][i],2)) throw std::runtime_error("characteristic congruence");
        if(mod(chi[i],2)!=1) throw std::runtime_error("characteristic parity");
    }
}
bool in_code(const std::array<int64_t,48>& y) {
    for(int j=0;j<24;++j) {
        int64_t s=0; for(int i=0;i<24;++i) s+=y[i]*S[i][j];
        if(mod(s-y[24+j],3)) return false;
    }
    return true;
}
int membership(const Row& y) {
    int norm=0; bool even=true, odd=true;
    for(int i=0;i<48;++i) { norm+=int(y[i])*y[i]; even &= mod(y[i],2)==0; odd &= mod(y[i]-glue[i],2)==0; }
    if(norm!=72) throw std::runtime_error("norm is not 72");
    std::array<int64_t,48> u{};
    if(even) {
        for(int i=0;i<48;++i) u[i]=y[i]/2;
        if(!in_code(u)) throw std::runtime_error("even residue outside code");
        int64_t q=0; for(auto a:u) q+=a*a;
        if(q%6) throw std::runtime_error("even sublattice parity");
        return 0;
    }
    if(odd) {
        for(int i=0;i<48;++i) u[i]=(y[i]-glue[i])/2;
        if(!in_code(u)) throw std::runtime_error("odd residue outside code");
        int64_t d=0; for(int i=0;i<48;++i) d+=u[i]*chi[i];
        if(d%6) throw std::runtime_error("odd glue congruence");
        return 1;
    }
    throw std::runtime_error("mixed coordinate parity");
}
int main(int argc,char**argv) {
  try {
    if(argc!=2) throw std::runtime_error("usage: check_p48 blocks.txt");
    model(); std::ifstream f(argv[1]); if(!f) throw std::runtime_error("cannot open input");
    std::map<int,std::vector<Row>> blocks; std::unordered_set<std::string> unique;
    unique.reserve(700000); uint64_t rows=0, even=0, odd=0, pairs=0;
    std::string line;
    while(std::getline(f,line)) {
        if(line.empty()||line[0]=='#') continue;
        std::istringstream is(line); int id; if(!(is>>id)||id<0) throw std::runtime_error("bad block id");
        Row y; std::string key;
        for(int j=0;j<48;++j) {
            int v; if(!(is>>v)||v< -8||v>8) throw std::runtime_error("bad integer coordinate");
            y[j]=int16_t(v); key.push_back(char(v+8));
        }
        std::string extra; if(is>>extra) throw std::runtime_error("trailing fields");
        if(!unique.insert(key).second) throw std::runtime_error("duplicate oriented row");
        membership(y)?++odd:++even;
        blocks[id].push_back(y); ++rows;
    }
    if(!rows) throw std::runtime_error("empty certificate");
    std::vector<size_t> sizes; std::ostringstream per;
    bool first=true;
    for(const auto& entry:blocks) {
        const auto& b=entry.second; int mx=-72;
        for(size_t i=0;i<b.size();++i) for(size_t j=i+1;j<b.size();++j) {
            int dot=0;
            for(int k=0;k<48;++k) dot+=int(b[i][k])*int(b[j][k]);
            if(dot>24) throw std::runtime_error("within-block inner product exceeds 24");
            if(dot>mx) mx=dot; ++pairs;
        }
        sizes.push_back(b.size());
        if(!first) per<<","; first=false;
        per<<"{\"block_id\":"<<entry.first<<",\"size\":"<<b.size()<<",\"max_dot\":"<<mx<<"}";
        std::cerr<<"checked block "<<entry.first<<" ("<<b.size()<<" rows)\n";
    }
    std::sort(sizes.rbegin(),sizes.rend());
    std::cout<<"{\"valid_finite_blocks\":true,\"ambient_minimum_proved\":false,\"world_record_priority_proved\":false,"
      <<"\"rows\":"<<rows<<",\"even_rows\":"<<even<<",\"odd_rows\":"<<odd
      <<",\"unordered_pairs_checked\":"<<pairs<<",\"blocks\":["<<per.str()<<"],\"sizes_desc\":[";
    for(size_t i=0;i<sizes.size();++i) std::cout<<(i?",":"")<<sizes[i];
    std::cout<<"],\"chi\":[";
    for(int i=0;i<48;++i) std::cout<<(i?",":"")<<chi[i];
    std::cout<<"],\"glue\":[";
    for(int i=0;i<48;++i) std::cout<<(i?",":"")<<glue[i];
    std::cout<<"]}\n";
  } catch(const std::exception& e) { std::cerr<<e.what()<<"\n"; return 1; }
}
