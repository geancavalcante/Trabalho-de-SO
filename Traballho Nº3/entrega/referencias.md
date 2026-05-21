---
title: "Referências"
subtitle: "System Design da Memória em Sistemas Operacionais"
author: "Gean Feitosa Cavalcante"
date: "2026"
documentclass: article
geometry: margin=2.5cm
fontsize: 11pt
linestretch: 1.3
---

# Referências

## Documentação oficial do Linux Kernel

KERNEL.ORG. **Page Tables — The Linux Kernel documentation**. Disponível em: <https://docs.kernel.org/mm/page_tables.html>. Acesso em: 2026.

KERNEL.ORG. **Memory Management — The Linux Kernel documentation**. Disponível em: <https://docs.kernel.org/admin-guide/mm/index.html>. Acesso em: 2026.

## Manuais do sistema (man pages)

KERRISK, Michael. **proc_pid_maps(5) — Linux manual page**. Disponível em: <https://man7.org/linux/man-pages/man5/proc_pid_maps.5.html>. Acesso em: 2026.

KERRISK, Michael. **proc_pid_smaps(5) — Linux manual page**. Disponível em: <https://man7.org/linux/man-pages/man5/proc_pid_smaps.5.html>. Acesso em: 2026.

KERRISK, Michael. **proc(5) — Linux manual page**. Disponível em: <https://man7.org/linux/man-pages/man5/proc.5.html>. Acesso em: 2026.

KERRISK, Michael. **vmstat(8) — Linux manual page**. Disponível em: <https://man7.org/linux/man-pages/man8/vmstat.8.html>. Acesso em: 2026.

KERRISK, Michael. **free(1) — Linux manual page**. Disponível em: <https://man7.org/linux/man-pages/man1/free.1.html>. Acesso em: 2026.

KERRISK, Michael. **top(1) — Linux manual page**. Disponível em: <https://man7.org/linux/man-pages/man1/top.1.html>. Acesso em: 2026.

## Artigos acadêmicos

CARLSON, T. E. et al. **What Do You Mean by Memory? When Engineers Are Lost in the Maze of Complexity**. Proceedings of the ACM. 2024. Disponível em: <https://dl.acm.org/doi/pdf/10.1145/3639477.3639735>. Acesso em: 2026.

KANTREIS, M. et al. **eBPF-mm: Userspace-guided memory management in Linux with eBPF**. arXiv preprint. 2024. Disponível em: <https://arxiv.org/html/2409.11220v1>. Acesso em: 2026.

AMIT, N.; TAI, A. **Skip TLB flushes for reused pages within mmap's**. arXiv preprint. 2024. Disponível em: <https://arxiv.org/pdf/2409.10946.pdf>. Acesso em: 2026.

WU, J. et al. **Non-volatile main memory management methods based on a file system**. PubMed Central. Disponível em: <https://pmc.ncbi.nlm.nih.gov/articles/PMC4162891/>. Acesso em: 2026.

## Observação sobre as fontes

As referências de **documentação oficial** (kernel.org e man7) sustentam todas as partes técnicas e práticas do trabalho — especialmente as seções sobre MMU, tabelas de páginas, `/proc/<pid>/maps`, `/proc/<pid>/smaps`, `vmstat` e o subsistema VM do Linux.

Os **artigos acadêmicos** foram utilizados para fortalecer a análise crítica, os *trade-offs* e a discussão sobre tendências modernas em gerenciamento de memória (eBPF, *TLB flush optimization*, memória não-volátil).
