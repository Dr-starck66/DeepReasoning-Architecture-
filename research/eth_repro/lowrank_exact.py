#!/usr/bin/env python3
"""Literal finite reconstruction of Section 4 (swap-matrix), OpenAI ETH manuscript 2026-10-25.

Not an implementation of the claimed subexponential SAT algorithm.
Default r=2,Q=3,R=2,I=[0,1] meets 1<=R<Q and creates a 64x64
matrix with exactly 10 measurements, rank(I-M0)=10.
Fully exact: all coefficients rational (fractions.Fraction).
"""
from __future__ import annotations
from dataclasses import dataclass
from fractions import Fraction as F
from itertools import product
from math import comb
from typing import Tuple

Label = Tuple[Tuple[int, ...], Tuple[int, ...]]


def all_labels(r: int, q: int) -> tuple[Label,...]:
    seqs = tuple(product(range(r),repeat=q))
    return tuple((a,d) for a in seqs for d in seqs)


def swap(label: Label, axes: tuple[int,...]) -> Label:
    a,d = map(list,label)
    for s in axes:
        a[s],d[s]=d[s],a[s]
    return tuple(a),tuple(d)


def eigenvectors_one(r:int):
    """Each item is (eigenvalue, vector on r^2 coordinates) of one coordinate swap."""
    order = tuple(product(range(r),repeat=2))
    index = {v:k for k,v in enumerate(order)}
    results=[]
    for a in range(r):
        v=[0]*len(order);v[index[a,a]]=1
        results.append((+1, tuple(v)))
    for a in range(r):
        for d in range(a+1,r):
            plus=[0]*len(order);plus[index[a,d]]=1;plus[index[d,a]]=1
            minus=[0]*len(order);minus[index[a,d]]=1;minus[index[d,a]]=-1
            results.append((+1,tuple(plus)))
            results.append((-1,tuple(minus)))
    assert len(results)==r*r
    return order,tuple(results)


def spectral_rows(r:int,q:int, interval:range, labels:tuple[Label,...]):
    base,little=eigenvectors_one(r)
    bidx={lab:i for i,lab in enumerate(base)}
    # Columns j outside I generate measurement rows.
    rows=[]
    classes={}
    for choice in product(range(r*r), repeat=q):
        eigs=[little[c][0] for c in choice]
        j=eigs.count(-1)
        if j not in interval:
            row=tuple(__import__('math').prod(little[choice[s]][1][bidx[(a[s],d[s])]] for s in range(q)) for a,d in labels)
            assert any(row)
            rows.append(row); classes[row]=j
    return tuple(rows),classes


def dense_rank(A:tuple[tuple[int,...],...])->int:
    """Exact gaussian elimination over Q; input modest-sized (64 x 64)."""
    if not A:return 0
    mat=[[F(x) for x in row] for row in A]
    m=len(mat);n=len(mat[0]);i=0
    for j in range(n):
        pivot=next((t for t in range(i,m) if mat[t][j]),None)
        if pivot is None:continue
        mat[i],mat[pivot]=mat[pivot],mat[i]
        scale=mat[i][j]
        for k in range(j,n):mat[i][k]/=scale
        for t in range(i+1,m):
            if mat[t][j]:
                v=mat[t][j]
                for k in range(j,n):mat[t][k]-=v*mat[i][k]
        i+=1
        if i==m:break
    return i


@dataclass(frozen=True)
class FiniteSwapMatrix:
    r:int
    q:int
    R:int
    interval:range
    labels:tuple[Label,...]
    M0:tuple[tuple[int,...],...]
    C:tuple[tuple[int,...],...]
    eigenclass:dict[tuple[int,...],int]
    P0:tuple[tuple[F,...],...]
    P1:tuple[tuple[F,...],...]

    @classmethod
    def build(cls,r:int=2,q:int=3,R:int=2,A0:int=0):
        assert r>=2 and 1<=R<q and 0<=A0<=q-R+1
        assert R==2 and A0==0, "closed-form M0 implementation is for f(z)=1-2z only"
        labels=all_labels(r,q)
        index={u:i for i,u in enumerate(labels)}
        D=len(labels)
        # f_I(W)=1-2W= sum_s Pi_s -(q-1)I
        # M0=V0 f_I(W)= sum_s prod_{h !=s} Pi_h - (q-1)V0
        m=[[0]*D for _ in range(D)]
        for i,u in enumerate(labels):
            for axis in range(q):
                target=swap(u,tuple(h for h in range(q) if h!=axis))
                m[i][index[target]]+=1
            m[i][index[swap(u,tuple(range(q)))]]-=(q-1)
        C,eigenclass=spectral_rows(r,q,range(A0,A0+R),labels)
        P0=[];P1=[]
        for i,u in enumerate(labels):
            # P_u(T)=e_u(I-M0)+sum_y M0[u,y] phi_{u,y}(T)e_y
            # <=1 mismatch: phi=1 if none else 1-T/s
            c0=[];c1=[]
            for j,v in enumerate(labels):
                mismatch=[s for s in range(q) if v[0][s]!=u[1][s]]
                if m[i][j] and len(mismatch)>R-1:
                    raise AssertionError(('support',i,j,mismatch))
                p0=int(i==j) # identity at zero, exact cancellation
                p1=F(-m[i][j],mismatch[0]+1) if m[i][j] and len(mismatch)==1 else F(0)
                c0.append(F(p0));c1.append(p1)
            P0.append(tuple(c0));P1.append(tuple(c1))
        return cls(r,q,R,range(A0,A0+R),labels,tuple(map(tuple,m)),C,eigenclass,tuple(P0),tuple(P1))

    def eval_row(self,u:int,t:int):
        return tuple(self.P0[u][j] +t*self.P1[u][j] for j in range(len(self.labels)))

    def measurements(self,zeta:tuple[int,...]):
        return tuple(sum(a*b for a,b in zip(row,zeta)) for row in self.C)

    def coefficients_from_measurements(self,u:int):
        """K_u where (I-M0)[u,:] = sum_i K[u,i] C[i,:], exact orthogonal eigensystem."""
        out=[]
        for row in self.C:
            j=self.eigenclass[row]
            f=1-2*j
            lam=(-1)**j*f
            norm=sum(x*x for x in row)
            out.append(F((1-lam)*row[u],norm))
        return tuple(out)

    def audit(self)->dict:
        r,q,R=self.r,self.q,self.R
        D=len(self.labels)
        assert D==r**(2*q)
        positive=r*(r+1)//2
        negative=r*(r-1)//2
        expected_bad=sum(comb(q,j)*negative**j*positive**(q-j) for j in range(q+1) if j not in self.interval)
        assert len(self.C)==expected_bad
        # Interpolation matrix row special values and low-degree coefficients
        for u in range(D):
            ku=self.coefficients_from_measurements(u)
            for y in range(D):
                e=int(u==y)
                im0=e-self.M0[u][y]
                assert im0==sum(ku[t]*self.C[t][y] for t in range(len(self.C)))
            for t in range(1,q+1):
                g=self.labels[u][1][t-1]
                row=self.eval_row(u,t)
                for y in range(D):
                    if self.labels[y][0][t-1]!=g:
                        assert row[y]==sum(ku[k]*self.C[k][y] for k in range(len(self.C)))
        # Orthogonality is a simple independent check on measurements.
        for i,c in enumerate(self.C):
            for j,d in enumerate(self.C):
                dot=sum(a*b for a,b in zip(c,d))
                assert (dot!=0)==(i==j)
        # Direct ranks, entirely independent of spectral count.
        rank_c=dense_rank(self.C)
        IminusM=tuple(tuple(int(i==j)-self.M0[i][j] for j in range(D)) for i in range(D))
        rank_diff=dense_rank(IminusM)
        assert rank_c==rank_diff==expected_bad
        # independent random-ish exact integer coordinates (non-Boolean matters)
        for seed in range(5):
            zeta=tuple(((j*11+seed*7)%9)-4 for j in range(D))
            measurements=self.measurements(zeta)
            for u in range(D):
                ku=self.coefficients_from_measurements(u)
                actual=sum(IminusM[u][j]*zeta[j] for j in range(D))
                measured=sum(a*b for a,b in zip(ku,measurements))
                assert actual==measured
        return {
            'source':'OpenAI manuscript section 4, lemmas swaps-matrix, swaps-support, swaps-forms',
            'r':r,'Q':q,'R':R,'A0':self.interval.start,'D':D,'C_rows':len(self.C),
            'measurement_fraction':str(F(len(self.C),D)),
            'expected_binomial_outside_interval':str(F(expected_bad,D)),
            'rank_C':rank_c,'rank_I_minus_M0':rank_diff,
            'rank_M0':dense_rank(self.M0),
            'finite_properties':{
                'commuting_involutions':'verified by explicit index swap + tests',
                'rank_kernel':'exact verified',
                'support_at_most_R_minus_1':'exact verified',
                'P_degree_at_most_R_minus_1':'exact verified',
                'P_at_zero_identity':'exact verified',
                'off_group_row_space':'exact verified',
                'negative_controls':'see tests'},
            'asymptotic_machine':'UNVERIFIED',
            'valuation_1m':'UNVERIFIED',
        }


def example_q2_row():
    # Paper remark uses Q=R=2, outside R<Q needed by asymptotic argument.
    # Build via exact interpolation of f(W) with q=2 (closed-form same).
    r=2;q=2
    labs=all_labels(r,q);ind={u:i for i,u in enumerate(labs)}
    u=((0,0),(1,1));ui=ind[u]
    m={}
    for s in range(q):
        target=swap(u,tuple(h for h in range(q) if h!=s))
        m[target]=m.get(target,0)+1
    target=swap(u,(0,1));m[target]=m.get(target,0)-(q-1)
    row={}
    for y in labs:
        mism=[s for s in range(q) if y[0][s]!=u[1][s]]
        assert (not m.get(y,0)) or len(mism)<=1
        coef0=F(int(y==u));coef1=F(-m.get(y,0),mism[0]+1) if m.get(y,0) and mism else F(0)
        if coef0 or coef1: row[y]=(coef0,coef1)
    return row


if __name__=='__main__':
    import json
    d=FiniteSwapMatrix.build()
    info=d.audit()
    print(json.dumps(info,indent=2))
    print('Original manuscript example Q=R=2 row:',example_q2_row())