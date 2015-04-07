from cffi import FFI
def link_clib(block_cell_name):
    ffi = FFI()
    ffi.cdef(r'''
/* --- primary CSparse routines and data structures ------------------------- */
typedef struct cs_sparse    /* matrix in compressed-column or triplet form */
{
    ptrdiff_t nzmax ;     /* maximum number of entries */
    ptrdiff_t m ;         /* number of rows */
    ptrdiff_t n ;         /* number of columns */
    ptrdiff_t *p ;        /* column pointers (size n+1) or col indices (size nzmax) */
    ptrdiff_t *i ;        /* row indices, size nzmax */
    double *x ;     /* numerical values, size nzmax */
    ptrdiff_t nz ;        /* # of entries in triplet matrix, -1 for compressed-col */
} cs ;

cs *cs_add (const cs *A, const cs *B, double alpha, double beta) ;
ptrdiff_t cs_cholsol (ptrdiff_t order, const cs *A, double *b) ;
cs *cs_compress (const cs *T) ;
ptrdiff_t cs_dupl (cs *A) ;
ptrdiff_t cs_entry (cs *T, ptrdiff_t i, ptrdiff_t j, double x) ;
ptrdiff_t cs_gaxpy (const cs *A, const double *x, double *y) ;
cs *cs_load (FILE *f) ;
ptrdiff_t cs_lusol (ptrdiff_t order, const cs *A, double *b, double tol) ;
cs *cs_multiply (const cs *A, const cs *B) ;
double cs_norm (const cs *A) ;
ptrdiff_t cs_print (const cs *A, ptrdiff_t brief) ;
ptrdiff_t cs_qrsol (ptrdiff_t order, const cs *A, double *b) ;
cs *cs_transpose (const cs *A, ptrdiff_t values) ;
/* utilities */
void *cs_calloc (ptrdiff_t n, size_t size) ;
void *cs_free (void *p) ;
void *cs_realloc (void *p, ptrdiff_t n, size_t size, ptrdiff_t *ok) ;
cs *cs_spalloc (ptrdiff_t m, ptrdiff_t n, ptrdiff_t nzmax, ptrdiff_t values, ptrdiff_t triplet) ;
cs *cs_spfree (cs *A) ;
ptrdiff_t cs_sprealloc (cs *A, ptrdiff_t nzmax) ;
void *cs_malloc (ptrdiff_t n, size_t size) ;

/* --- secondary CSparse routines and data structures ----------------------- */
typedef struct cs_symbolic  /* symbolic Cholesky, LU, or QR analysis */
{
    ptrdiff_t *pinv ;     /* inverse row perm. for QR, fill red. perm for Chol */
    ptrdiff_t *q ;        /* fill-reducing column permutation for LU and QR */
    ptrdiff_t *parent ;   /* elimination tree for Cholesky and QR */
    ptrdiff_t *cp ;       /* column pointers for Cholesky, row counts for QR */
    ptrdiff_t *leftmost ; /* leftmost[i] = min(find(A(i,:))), for QR */
    ptrdiff_t m2 ;        /* # of rows for QR, after adding fictitious rows */
    double lnz ;    /* # entries in L for LU or Cholesky; in V for QR */
    double unz ;    /* # entries in U for LU; in R for QR */
} css ;

typedef struct cs_numeric   /* numeric Cholesky, LU, or QR factorization */
{
    cs *L ;         /* L for LU and Cholesky, V for QR */
    cs *U ;         /* U for LU, R for QR, not used for Cholesky */
    ptrdiff_t *pinv ;     /* partial pivoting for LU */
    double *B ;     /* beta [0..n-1] for QR */
} csn ;

typedef struct cs_dmperm_results    /* cs_dmperm or cs_scc output */
{
    ptrdiff_t *p ;        /* size m, row permutation */
    ptrdiff_t *q ;        /* size n, column permutation */
    ptrdiff_t *r ;        /* size nb+1, block k is rows r[k] to r[k+1]-1 in A(p,q) */
    ptrdiff_t *s ;        /* size nb+1, block k is cols s[k] to s[k+1]-1 in A(p,q) */
    ptrdiff_t nb ;        /* # of blocks in fine dmperm decomposition */
    ptrdiff_t rr [5] ;    /* coarse row decomposition */
    ptrdiff_t cc [5] ;    /* coarse column decomposition */
} csd ;

ptrdiff_t *cs_amd (ptrdiff_t order, const cs *A) ;
csn *cs_chol (const cs *A, const css *S) ;
csd *cs_dmperm (const cs *A, ptrdiff_t seed) ;
ptrdiff_t cs_droptol (cs *A, double tol) ;
ptrdiff_t cs_dropzeros (cs *A) ;
ptrdiff_t cs_happly (const cs *V, ptrdiff_t i, double beta, double *x) ;
ptrdiff_t cs_ipvec (const ptrdiff_t *p, const double *b, double *x, ptrdiff_t n) ;
ptrdiff_t cs_lsolve (const cs *L, double *x) ;
ptrdiff_t cs_ltsolve (const cs *L, double *x) ;
csn *cs_lu (const cs *A, const css *S, double tol) ;
cs *cs_permute (const cs *A, const ptrdiff_t *pinv, const ptrdiff_t *q, ptrdiff_t values) ;
ptrdiff_t *cs_pinv (const ptrdiff_t *p, ptrdiff_t n) ;
ptrdiff_t cs_pvec (const ptrdiff_t *p, const double *b, double *x, ptrdiff_t n) ;
csn *cs_qr (const cs *A, const css *S) ;
css *cs_schol (ptrdiff_t order, const cs *A) ;
css *cs_sqr (ptrdiff_t order, const cs *A, ptrdiff_t qr) ;
cs *cs_symperm (const cs *A, const ptrdiff_t *pinv, ptrdiff_t values) ;
ptrdiff_t cs_updown (cs *L, ptrdiff_t sigma, const cs *C, const ptrdiff_t *parent) ;
ptrdiff_t cs_usolve (const cs *U, double *x) ;
ptrdiff_t cs_utsolve (const cs *U, double *x) ;
/* utilities */
css *cs_sfree (css *S) ;
csn *cs_nfree (csn *N) ;
csd *cs_dfree (csd *D) ;

/* --- tertiary CSparse routines -------------------------------------------- */
ptrdiff_t *cs_counts (const cs *A, const ptrdiff_t *parent, const ptrdiff_t *post, ptrdiff_t ata) ;
double cs_cumsum (ptrdiff_t *p, ptrdiff_t *c, ptrdiff_t n) ;
ptrdiff_t cs_dfs (ptrdiff_t j, cs *G, ptrdiff_t top, ptrdiff_t *xi, ptrdiff_t *pstack, const ptrdiff_t *pinv) ;
ptrdiff_t cs_ereach (const cs *A, ptrdiff_t k, const ptrdiff_t *parent, ptrdiff_t *s, ptrdiff_t *w) ;
ptrdiff_t *cs_etree (const cs *A, ptrdiff_t ata) ;
ptrdiff_t cs_fkeep (cs *A, ptrdiff_t (*fkeep) (ptrdiff_t, ptrdiff_t, double, void *), void *other) ;
double cs_house (double *x, double *beta, ptrdiff_t n) ;
ptrdiff_t cs_leaf (ptrdiff_t i, ptrdiff_t j, const ptrdiff_t *first, ptrdiff_t *maxfirst, ptrdiff_t *prevleaf,
    ptrdiff_t *ancestor, ptrdiff_t *jleaf) ;
ptrdiff_t *cs_maxtrans (const cs *A, ptrdiff_t seed) ;
ptrdiff_t *cs_post (const ptrdiff_t *parent, ptrdiff_t n) ;
ptrdiff_t *cs_randperm (ptrdiff_t n, ptrdiff_t seed) ;
ptrdiff_t cs_reach (cs *G, const cs *B, ptrdiff_t k, ptrdiff_t *xi, const ptrdiff_t *pinv) ;
ptrdiff_t cs_scatter (const cs *A, ptrdiff_t j, double beta, ptrdiff_t *w, double *x, ptrdiff_t mark,
    cs *C, ptrdiff_t nz) ;
csd *cs_scc (cs *A) ;
ptrdiff_t cs_spsolve (cs *G, const cs *B, ptrdiff_t k, ptrdiff_t *xi, double *x,
    const ptrdiff_t *pinv, ptrdiff_t lo) ;
ptrdiff_t cs_tdfs (ptrdiff_t j, ptrdiff_t k, ptrdiff_t *head, const ptrdiff_t *next, ptrdiff_t *post,
    ptrdiff_t *stack) ;
/* utilities */
csd *cs_dalloc (ptrdiff_t m, ptrdiff_t n) ;
csd *cs_ddone (csd *D, cs *C, void *w, ptrdiff_t ok) ;
cs *cs_done (cs *C, void *w, void *x, ptrdiff_t ok) ;
ptrdiff_t *cs_idone (ptrdiff_t *p, cs *C, void *w, ptrdiff_t ok) ;
csn *cs_ndone (csn *N, cs *C, void *w, void *x, ptrdiff_t ok) ;''')
    C = ffi.dlopen('%DYLIB_FILE%')
    return ffi, C
