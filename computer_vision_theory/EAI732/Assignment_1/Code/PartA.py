import scipy
from scipy.io import loadmat
import pandas as pd
import math
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import matplotlib.gridspec as gridspec
from scipy.stats import norm
import os

def least_squares_fit(x, y, order):
    """Solve normal equations: c = (V^T V)^{-1} V^T y."""
    V = build_vandermonde(x, order)
    VtV = V.T @ V
    Vty = V.T @ y
    coeffs = np.linalg.solve(VtV, Vty)  # more stable than explicit inverse
    return coeffs     

def build_vandermonde(x, order):
    """Build Vandermonde matrix: columns are x^0, x^1, ..., x^order."""
    return np.column_stack([x**i for i in range(order + 1)])

def eval_poly(x, coeffs):
    """Evaluate polynomial with ascending-order coefficients."""
    return sum(c * x**i for i, c in enumerate(coeffs))

def mle_analytic(x, y, order):
    V = build_vandermonde(x, order)
    VtV = V.T @ V
    Vty = V.T @ y
    coeffs = np.linalg.solve(VtV, Vty)

    residuals = y - V @ coeffs
    n = len(y)
    sigma2_mle = np.sum(residuals**2) / n   # MLE estimate of sigma² (note: biased)

    p = order + 1
    sigma2_unbiased = np.sum((y - V @ coeffs)**2) / (len(y) - p)
    return V, coeffs, sigma2_unbiased

def bayesian_approach(x, y, order, alpha, sigma):
    V = build_vandermonde(x, order)
    # ============================================================
    # 2. ZERO-MEAN GAUSSIAN PRIOR
    #    p(c) = N(0, alpha^2 * I)
    #    => each coefficient independently ~ N(0, alpha^2)
    #    => log p(c) = -1/(2*alpha^2) * ||c||^2  + const
    # ============================================================

    lambda_reg = sigma**2/alpha**2
    # ============================================================
    # 3. POSTERIOR COVARIANCE  S
    #    From Bayes' theorem with conjugate Gaussian prior:
    #
    #    S^{-1} = (1/sigma^2) * V^T V  +  (1/alpha^2) * I
    #             ^-- data precision       ^-- prior precision
    #
    #    S       = inv(S^{-1})
    # ============================================================

    S_inv = (1/sigma**2) * (V.T @ V) + (1/alpha**2) * np.eye(order + 1)
    S = np.linalg.inv(S_inv)
    print(np.round(S, 5))

    # ============================================================
    # 4. POSTERIOR MEAN  m  =  E[c | y]
    #    m = (1/sigma^2) * S @ V^T @ y
    
    #    This is ALSO the MAP estimate for a Gaussian posterior
    #    because the Gaussian is symmetric — mode = mean.
    # ============================================================

    m = (1/sigma**2) * S @ V.T @ y

    # ============================================================
    # 5. MAP ESTIMATE  c_map
    #    MAP = argmax p(c|y)
    #        = argmin  ||y - Vc||^2/sigma^2  +  ||c||^2/alpha^2
    #        = (V^T V  +  lambda*I)^{-1}  V^T y       (Ridge regression)
    #
    #    For a Gaussian posterior: MAP == posterior mean exactly.
    # ============================================================
    A_map  = V.T @ V  +  lambda_reg * np.eye(order + 1)
    c_map  = np.linalg.solve(A_map, V.T @ y)     # shape: (P,)
    return m, S, V, c_map

def compute_posterior(x, y, order, alpha, sigma):
    V = build_vandermonde(x, order)
    S_inv = (1/sigma**2) * (V.T @ V) + (1/alpha**2) * np.eye(order + 1)
    S = np.linalg.inv(S_inv)
    m = (1/sigma**2) * S @ V.T @ y

    return m, S, V

def log_marginal_likelihood(N, x, y, order, alpha, sigma):
    # ============================================================
    # 2. MARGINAL LIKELIHOOD  p(y | order, alpha, sigma)
    #    Integrating out the coefficients c analytically:
    #    p(y | M) = integral p(y|c,M) p(c|M) dc
    #
    #    For Gaussian likelihood + Gaussian prior this is:
    #    p(y | M) = N(y ; 0 , C)
    #    where the marginal covariance is:
    #    C = sigma^2 * I  +  alpha^2 * V V^T       shape: (N, N)
    #
    #    Log marginal likelihood:
    #    log p(y|M) = -N/2 * log(2*pi)
    #                 - 1/2 * log det(C)
    #                 - 1/2 * y^T C^{-1} y
    #
    #    Equivalent closed form using posterior quantities:
    #    log p(y|M) = -N/2 * log(2*pi*sigma^2)
    #                 - 1/2 * log det(S^{-1}) + 1/2 * log det((1/alpha^2)*I)
    #                 - 1/(2*sigma^2) * (y^T y  -  m^T S^{-1} m)
    #
    #    Which simplifies to:
    #    log p(y|M) = -N/2 * log(2*pi*sigma^2)
    #                 + 1/2 * log det(S)  -  p/2 * log(alpha^2)   <- prior normalisation
    #                 - 1/(2*sigma^2) * ||y||^2                    <- data fit term
    #                 + 1/(2*sigma^2)^2 * m^T S^{-1} m            <- posterior gain
    # ============================================================

    N = len(y)
    p = order + 1
    m, S, V = compute_posterior(x, y, order, alpha, sigma)

    # ── Step 1: build the full N×N marginal covariance ───────────────────────
    # C = sigma^2 * I  +  alpha^2 * V V^T
    # Each entry C[i,j] = sigma^2 * delta(i,j)  +  alpha^2 * v(x_i)^T v(x_j)
    # where v(x_i) = [1, x_i, x_i^2, ..., x_i^p] is the i-th row of V
    C = sigma**2 * np.eye(N)  +  alpha**2 * (V @ V.T)

    # ── Step 2: log determinant of C ─────────────────────────────────────────
    # np.linalg.slogdet returns (sign, log|det(C)|)
    # C is SPD so sign should always be +1
    sign, log_det_C = np.linalg.slogdet(C)

    # ── Step 3: invert C directly ────────────────────────────────────────────
    # This is the expensive step: O(N^3) full matrix inversion
    C_inv = np.linalg.inv(C)

    # ── Step 4: quadratic form  y^T C^{-1} y ────────────────────────────────
    quadratic = y @ C_inv @ y

    # ── Assemble log marginal likelihood ─────────────────────────────────────
    log_ml = -0.5 * N * np.log(2 * np.pi) \
             -0.5 * log_det_C \
             -0.5 * quadratic

    return log_ml, m, S, V

# ==========================================
# PART A: QUESTIONS 1 -> 10
# ==========================================

# ── Approach 1: Least Squares Algorithm to minimise error ─────────────────
def question1(df, order):
    w = least_squares_fit(df.index, df["y"], order)
    w = np.round(w, 4)
    print(w)

    # Plot 
    x_plot = np.linspace(df.index.min(), df.index.max(), 10)
    y_scratch = eval_poly(x_plot, w)

    # # Verify with library
    # w_lib = np.polyfit(df.index, df["y"], order)[::-1]
    # w_lib = np.round(w_lib, 4)
    # y_test = eval_poly(x_plot, w_lib)
    # print(w_lib)

    plt.figure(figsize=(10, 6))
    plt.scatter(df.index, df["y"], s=20, alpha=0.5, label="Noisy data", color="gray")
    plt.plot(x_plot, y_scratch,   "r-",  lw=2,   label="Least Squares Approach")
    # plt.plot(x_plot, y_test,   "g-",  lw=2,   label="Least Squares Library")
    plt.legend()
    plt.title(f"Polynomial Fitting {order}th Order: Least Squares")
    plt.xlabel("x"); plt.ylabel("y")
    plt.tight_layout()
    plt.savefig(f"poly_fit_{order}.pdf", dpi=150)
    plt.show()

# ── Approach 2: Analytic MLE (identical to normal equations) ─────────────────
# Maximising log-likelihood over c gives the same normal equations as least squares
def question2(df, order):
    x_plot = np.linspace(df.index.min(), df.index.max(), 10)
    V, w, sigma2_mle = mle_analytic(x_plot, df["y"], order)

    plt.figure(figsize=(10, 6))
    plt.scatter(df.index, df["y"], s=20, alpha=0.5, color='gray', label='Noisy data')
    plt.plot(x_plot, V @ w,  'r-',  lw=2,   label='MLE Approach')
    # plt.plot(x_plot, V_plot @ coeffs_numerical, 'b--', lw=2,   label='Numerical MLE (Gaussian)')
    # plt.plot(x_plot, V_plot @ coeffs_laplace,   'g:',  lw=2.5, label='Numerical MLE (Laplace / L1)')
    plt.legend()
    plt.title(f"Polynomial Fitting {order}th Order: MLE")
    plt.xlabel("x"); plt.ylabel("y")
    plt.tight_layout()
    plt.savefig(f"mle_fit_{order}.pdf", dpi=150)
    plt.show()

# ── Approach 3: Bayesian Approach ─────────────────
def question3(df, order):
    alpha = 0.005      # prior std  — how wide our prior belief is
    sigma = 1/11.1      # noise std  — assumed known (= TRUE_SIGMA here)
    m, S, V_plot, c_map = bayesian_approach(df.index, df["y"], order, alpha, sigma)

    post_var = np.diag(S)          # marginal variance per coefficient
    post_std = np.sqrt(post_var)   # marginal std per coefficient
    n_samples = len(df.index)
    x_plot = np.linspace(df.index.min(), df.index.max(), n_samples)

    coeff_samples = np.random.multivariate_normal(m, S, size=n_samples)
    curve_samples = V_plot @ coeff_samples.T

    mean_curve = V_plot @ m
    param_var = np.array([v @ S @ v for v in V_plot])   # parameter uncertainty
    pred_var = sigma**2 + param_var                     # total predictive variance
    pred_std = np.sqrt(pred_var)
    c_mle = np.linalg.solve(V_plot.T @ V_plot, V_plot.T @ df["y"])
    mle_curve = V_plot @ c_mle
    
    # --- Panel A: Fit + credible interval ---
    plt.figure(figsize=(10, 6))
    for i in range(0, n_samples, 6):
        plt.plot(x_plot, curve_samples[:, i], color='steelblue', alpha=0.04, lw=0.8)
    plt.fill_between(x_plot,
                        mean_curve - 1.96*pred_std,
                        mean_curve + 1.96*pred_std,
                        alpha=0.18, color='steelblue', label='95% predictive CI')
    plt.fill_between(x_plot,
                        mean_curve - 1.96*np.sqrt(param_var),
                        mean_curve + 1.96*np.sqrt(param_var),
                        alpha=0.28, color='royalblue', label='95% parameter CI')
    # ax_fit.plot(x_plot, V_plot @ np.array(TRUE_COEFFS), 'k--', lw=1.5, label='true polynomial')
    plt.plot(x_plot, mle_curve,   color='tomato',    lw=1.5, ls=':', label='MLE (no prior)')
    plt.plot(x_plot, mean_curve,  color='royalblue', lw=2.0, label='posterior mean = MAP')
    plt.scatter(x_plot, df["y"], s=18, color='gray', alpha=0.6, zorder=5, label='noisy data')
    plt.legend()
    plt.title(f"Polynomial Fitting {order}th Order: Bayesian Approach (zero-mean Gaussian prior)")
    plt.xlabel('x')
    plt.ylabel('y')
    plt.savefig(f"bayesian_fit_{order}.pdf", dpi=150)
    plt.show()

def question6(df, N, alpha, sigma):
    orders = list(range(0, 10))   # test orders 0 through 9
    log_mls = []
    fits = {}

    for order in orders:
        lml, m, S, V_plot = log_marginal_likelihood(N, df.index, df["y"], order, alpha, sigma)
        log_mls.append(lml)
        fits[order] = {
            'mean': V_plot @ m,
            'std':  np.sqrt(np.array([v @ S @ v for v in V_plot])),
            'm':    m,
            'S':    S
        }

    log_mls = np.array(log_mls)
    best_order = orders[np.argmax(log_mls)]

    # ============================================================
    # 6. PLOTTING
    # ============================================================
    plt.figure(figsize=(10, 6))
    
    # --- Panel A: Log marginal likelihood vs order ---
    plt.plot(orders, log_mls, 'o-', color='b', lw=2, ms=8, zorder=3)
    plt.axvline(best_order, color='r', lw=1.5, ls='--',
                label=f'best order = {best_order}')
    # ax_lml.axvline(TRUE_ORDER, color='black', lw=1.5, ls=':',
    #             label=f'true order = {TRUE_ORDER}')
    for o, lml in zip(orders, log_mls):
        plt.annotate(f'{lml:.1f}', (o, lml),
                        textcoords='offset points', xytext=(0, 8),
                        ha='center')
    plt.xticks(orders)
    plt.xlabel('model order (polynomial degree)')
    plt.ylabel('log p(y | M)')
    plt.title('Marginal likelihood vs model order')
    plt.legend()
    # plt.grid(True, alpha=0.3)
    plt.savefig(f"bayesian_model_selection.pdf", dpi=150)
    plt.show()

    question3(df, best_order)

def question7(df, N, alpha, sigma):
    orders = list(range(0, 10))   # test orders 0 through 9
    log_mls = []
    for o in orders:
        log_ml, m, S, V = log_marginal_likelihood(N, df.index, df["y"], o, alpha, sigma)
        log_mls.append(log_ml)

    # Softmax for numerical stability
    log_mls_shifted = log_mls - np.max(log_mls)
    unnorm = np.exp(log_mls_shifted)
    model_weights = unnorm/unnorm.sum()

    n_samples = len(df.index)
    x_plot = np.linspace(df.index.min(), df.index.max(), n_samples)
    
    per_model = {}
    for o in orders:
        m_k, S_k, _ = compute_posterior(df.index, df["y"], o, alpha, sigma)
        V_plot = build_vandermonde(x_plot, o)

        mu_k = V_plot @ m_k
        var_k = sigma**2 + np.array([v @ S_k @ v for v in V_plot])
        per_model[o] = {'mu': mu_k, 'var': var_k, 'weight': model_weights[o]}

    bma_mean = sum(per_model[o]['weight'] * per_model[o]['mu']
               for o in orders)                                 # (300,)
 
    # within-model variance (aleatoric + parameter uncertainty per model)
    within_var = sum(per_model[o]['weight'] * per_model[o]['var']
                    for o in orders)                               # (300,)
    
    # between-model variance (model disagreement — epistemic)
    between_var = sum(per_model[o]['weight'] * (per_model[o]['mu'] - bma_mean)**2
                    for o in orders)                              # (300,)
    
    bma_var = within_var + between_var                             # total variance
    bma_std = np.sqrt(bma_var)                                     # total std
    
    within_std  = np.sqrt(within_var)
    between_std = np.sqrt(between_var)

    # ── Panel B: individual model predictive means (weighted by opacity)
    plt.figure(figsize=(10, 6))
    cmap = plt.cm.viridis(np.linspace(0.1, 0.9, len(orders)))
    for o in orders:
        w   = per_model[o]['weight']
        mu  = per_model[o]['mu']
        std = np.sqrt(per_model[o]['var'])
        if w > 1e-4:
            plt.plot(x_plot, mu, color=cmap[o], lw=1.5, alpha=min(1.0, w*4 + 0.1),
                        label=f'order {o}  (w={w:.3f})')
            plt.fill_between(x_plot, mu - std, mu + std,
                                color=cmap[o], alpha=w * 0.8)
    plt.scatter(df.index, df["y"], s=15, color='gray', alpha=0.4, zorder=5)
    plt.title('Per-model predictive distributions\n(opacity ∝ model weight)')
    plt.xlabel('x')
    plt.ylabel('y')
    plt.legend()
    plt.savefig(f"BMA_pred_dist.pdf", dpi=150)
    plt.show()

    plt.figure(figsize=(10, 6))
    plt.fill_between(x_plot,
                        bma_mean - 2*bma_std,
                        bma_mean + 2*bma_std,
                        alpha=0.15, color='steelblue', label='BMA ±2 std (total)')
    plt.fill_between(x_plot,
                        bma_mean - bma_std,
                        bma_mean + bma_std,
                        alpha=0.30, color='steelblue', label='BMA ±1 std (total)')
    plt.plot(x_plot, bma_mean,  color='steelblue', lw=2.5, label='BMA mean')
    plt.scatter(df.index, df["y"], s=18, color='gray', alpha=0.5, zorder=5, label='data')

    # overlay best single model for comparison
    best_order = orders[np.argmax(model_weights)]
    plt.plot(x_plot, per_model[best_order]['mu'],
                color='tomato', lw=1.5, ls='--',
                label=f'best single model (order {best_order})')
    plt.title('Bayesian model averaging — predictive mixture distribution\n'
                    'E[y*] = Σ_k w_k μ_k(x*)     Var[y*] = E[Var] + Var[E]')
    plt.xlabel('x')
    plt.ylabel('y')
    plt.legend()
    plt.savefig(f"BMA_pred_dist_best.pdf", dpi=150)
    plt.show()
 
if __name__ == "__main__":
    parent = os.path.dirname(os.getcwd())
    dataset_path = "/EAI-Coursework/Database"
    dataset = "dataset1"
    match dataset:
        case "dataset1":
            data = loadmat(parent + dataset_path + '/Dataset_1.mat')
            clean_data = {k: v for k, v in data.items() if not k.startswith('__')}
            if clean_data:
                try:
                    df = pd.DataFrame(data["y"].flatten(), columns=["y"])
                except Exception as e:
                    print("Could not convert to Dataframe:", e)
            
            order = 9
            question1(df, order)
            question2(df, order)
            question3(df, order)
        
        case "dataset2": 
            data = loadmat(parent + dataset_path + '/Dataset_2.mat')
            clean_data = {k: v for k, v in data.items() if not k.startswith('__')}
            if clean_data:
                try:
                    df = pd.DataFrame(data["y"].flatten(), columns=["y"])
                except Exception as e:
                    print("Could not convert to Dataframe:", e)
            N = len(df.index)
            alpha = 0.005 # 2    # prior std  — how wide our prior belief is ->  2
            sigma = 1/11.1  # noise std  — assumed known (= TRUE_SIGMA here) -> 1.5

            question6(df, N, alpha, sigma)
            question7(df, N, alpha, sigma)