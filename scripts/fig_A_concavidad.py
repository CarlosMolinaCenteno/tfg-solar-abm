"""Test conjetura concavidad / esquinas para el cártel.

Para varios gamma_G crecientes, evalúa pi(f) y d2pi/df2 sobre [0,1]
con el resto de parámetros del banco INTERIOR. Detecta:
  - dónde se rompe la concavidad (d2pi/df2 > 0)
  - dónde cae el óptimo (interior vs esquina)
  - cuántos máximos locales hay
"""
from __future__ import annotations

import os
import sys
import numpy as np
import matplotlib.pyplot as plt

sys.stdout.reconfigure(encoding="utf-8")

# Parámetros base (PARAMS_INTERIOR del banco, sin c0)
N = 30
D_M = 80.0
D_E = 120.0
c = 2.5
alpha_M = 0.7
alpha_E = 0.3
eta = 0.9
alpha_G = 0.5

# Producciones brutas agregadas
qM_tilde = N * alpha_M * c  # 52.5
qE_tilde = N * alpha_E * c  # 22.5
print(f"qM_tilde = {qM_tilde}, qE_tilde = {qE_tilde}")
print(f"D_M = {D_M}, D_E = {D_E}")


def pi_and_derivs(f, gamma_G):
    """Devuelve pi(f), dpi/df y d2pi/df2 para vector f."""
    qM = (1.0 - f) * qM_tilde
    qE = qE_tilde + eta * f * qM_tilde
    gM = D_M - qM
    gE = D_E - qE
    PM = alpha_G * gM**gamma_G
    PE = alpha_G * gE**gamma_G
    pi = PM * qM + PE * qE
    # Derivadas con respecto a f
    # dqM/df = -qM_tilde, dqE/df = eta*qM_tilde
    # dgM/df = qM_tilde, dgE/df = -eta*qM_tilde
    dPM = alpha_G * gamma_G * gM ** (gamma_G - 1) * qM_tilde
    dPE = -alpha_G * gamma_G * eta * gE ** (gamma_G - 1) * qM_tilde
    dpi = dPM * qM + PM * (-qM_tilde) + dPE * qE + PE * (eta * qM_tilde)
    # Segunda derivada
    # d2PM/df2 = alpha_G * gamma_G * (gamma_G-1) * gM^(gamma_G-2) * qM_tilde^2
    d2PM = alpha_G * gamma_G * (gamma_G - 1) * gM ** (gamma_G - 2) * qM_tilde**2
    d2PE = alpha_G * gamma_G * (gamma_G - 1) * gE ** (gamma_G - 2) * (eta * qM_tilde) ** 2
    # d²(P·q)/df² = d²P·q + 2·dP·dq + 0  (porque d²q/df² = 0)
    d2pi_M = d2PM * qM + 2 * dPM * (-qM_tilde)
    d2pi_E = d2PE * qE + 2 * dPE * (eta * qM_tilde)
    d2pi = d2pi_M + d2pi_E
    return pi, dpi, d2pi, qM, gM, qE, gE


# Experimento: variar gamma_G
gamma_values = [1.3, 2.0, 3.0, 5.0]
f_grid = np.linspace(0.001, 0.999, 2001)

fig, axes = plt.subplots(2, 4, figsize=(18, 8))

for col, gamma_G in enumerate(gamma_values):
    pi, dpi, d2pi, qM, gM, qE, gE = pi_and_derivs(f_grid, gamma_G)

    # Encontrar óptimo (búsqueda exhaustiva por grid fino + comparar bordes)
    f_star_idx = np.argmax(pi)
    f_star = f_grid[f_star_idx]
    pi_star = pi[f_star_idx]

    pi_borde_0 = pi[0]
    pi_borde_1 = pi[-1]

    # ¿Es esquina?
    es_esquina = (f_star < 0.005) or (f_star > 0.995)

    # ¿Donde se rompe concavidad?
    convex_region = d2pi > 0
    f_convex = f_grid[convex_region]
    if len(f_convex) > 0:
        f_convex_min = f_convex.min()
        f_convex_max = f_convex.max()
    else:
        f_convex_min = f_convex_max = None

    # Ratios q/g en los extremos
    ratioM_0 = qM[0] / gM[0]
    ratioM_1 = qM[-1] / gM[-1]
    ratioE_0 = qE[0] / gE[0]
    ratioE_1 = qE[-1] / gE[-1]
    umbral = 2.0 / (gamma_G - 1)

    print()
    print(f"=== gamma_G = {gamma_G} ===")
    print(f"  Umbral 2/(gamma_G-1) = {umbral:.3f}")
    print(f"  q^M/g^M: f=0 -> {ratioM_0:.3f}, f=1 -> {ratioM_1:.3f}")
    print(f"  q^E/g^E: f=0 -> {ratioE_0:.3f}, f=1 -> {ratioE_1:.3f}")
    print(f"  ¿Hay region convexa? {'SI' if len(f_convex) > 0 else 'no'}")
    if f_convex_min is not None:
        print(f"     Region convexa: f en [{f_convex_min:.3f}, {f_convex_max:.3f}]")
    print(f"  f* = {f_star:.4f}, pi(f*) = {pi_star:.2f}")
    print(f"  pi(0) = {pi_borde_0:.2f}, pi(1) = {pi_borde_1:.2f}")
    print(f"  ¿Esquina? {'SI' if es_esquina else 'no (interior)'}")

    # Plot pi(f)
    ax_pi = axes[0, col]
    ax_pi.plot(f_grid, pi, 'b-', lw=1.5)
    ax_pi.axvline(f_star, color='red', linestyle='--', alpha=0.7,
                  label=f'f* = {f_star:.3f}')
    ax_pi.set_xlabel('f')
    ax_pi.set_ylabel('pi(f)')
    ax_pi.set_title(f'gamma_G = {gamma_G}, umbral q/g < {umbral:.2f}')
    ax_pi.legend(fontsize=8)
    ax_pi.grid(alpha=0.3)

    # Plot d2pi/df2
    ax_d2 = axes[1, col]
    ax_d2.plot(f_grid, d2pi, 'g-', lw=1.5)
    ax_d2.axhline(0, color='black', linestyle='-', alpha=0.5)
    if len(f_convex) > 0:
        ax_d2.axvspan(f_convex_min, f_convex_max, alpha=0.2, color='red',
                     label=f'convexa: [{f_convex_min:.2f}, {f_convex_max:.2f}]')
        ax_d2.legend(fontsize=8)
    ax_d2.set_xlabel('f')
    ax_d2.set_ylabel('d2pi/df2')
    ax_d2.set_title(f'segunda derivada')
    ax_d2.grid(alpha=0.3)

plt.tight_layout()
out_path = os.path.join(os.path.dirname(__file__), '..', 'figures', 'fig_A_concavidad.png')
plt.savefig(out_path, dpi=110, bbox_inches='tight')
print(f"\nFigura: {out_path}")
