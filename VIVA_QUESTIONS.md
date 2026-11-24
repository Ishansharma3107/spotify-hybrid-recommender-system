# Viva questions and answers

1. **Why combine two models?** Audio captures how tracks sound. Listening histories capture what people tend to play together.
2. **Why cosine similarity?** It compares the direction of vectors, reducing sensitivity to their overall magnitude.
3. **How do you handle cold start?** A track without sampled listeners uses audio similarity. Discovery provides a popularity baseline with no seed.
4. **Why use a sparse matrix?** Most listener–track pairs have no observations. CSR stores observed values and their positions.
5. **What does the slider change?** It changes the collaborative weight in the hybrid score. At zero the score uses audio. At one it uses collaborative cosine when available.
6. **How was leakage reduced?** Item similarities were built with training listeners. Test users were reserved for evaluation.
7. **What is Recall@10 here?** The fraction of held-out profiles whose single target appears in the first ten recommendations.
8. **What is the difference between MRR and NDCG?** Both reward higher ranks. With one relevant item, MRR discounts by rank and NDCG discounts by the logarithm of rank plus one.
9. **What does DVC provide?** It tracks stage inputs and outputs and lets the pipeline reuse or regenerate artifacts.
10. **What does feedback change?** Favorites are saved and hidden tracks are excluded. The offline models train on the public sample.
