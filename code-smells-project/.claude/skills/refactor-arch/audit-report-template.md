# Template de Relatório de Auditoria

Use este template exato na saída da Fase 2. Preencha cada campo com os dados reais do projeto analisado.
Findings devem ser ordenados: CRITICAL → HIGH → MEDIUM → LOW.

---

```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: <nome-do-projeto>
Stack:   <Linguagem> + <Framework versão>
Files:   <N> analyzed | ~<LOC> lines of code

Summary
CRITICAL: <N> | HIGH: <N> | MEDIUM: <N> | LOW: <N>

Findings

[CRITICAL] <Nome do Anti-Pattern>
File: <caminho/do/arquivo.py>:<linha-início>-<linha-fim>
Description: <descrição concisa e factual do problema encontrado>
Impact: <consequência direta se não corrigido>
Recommendation: <ação corretiva específica>

[CRITICAL] <Nome do Anti-Pattern>
File: <caminho/do/arquivo.py>:<linha>
Description: <...>
Impact: <...>
Recommendation: <...>

[HIGH] <Nome do Anti-Pattern>
File: <caminho/do/arquivo.py>:<linha-início>-<linha-fim>
Description: <...>
Impact: <...>
Recommendation: <...>

[MEDIUM] <Nome do Anti-Pattern>
File: <caminho/do/arquivo.py>:<linha>
Description: <...>
Impact: <...>
Recommendation: <...>

[LOW] <Nome do Anti-Pattern>
File: <caminho/do/arquivo.py>:<linha>
Description: <...>
Impact: <...>
Recommendation: <...>

================================
Total: <N> findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
```

---

## Regras de Preenchimento

1. **File:** sempre usar caminho relativo à raiz do projeto + número de linha exato. Se abrange um bloco, usar `linha-início:linha-fim`.
2. **Description:** factual, sem julgamento. Descrever o que foi encontrado, não o que deveria existir.
3. **Impact:** consequência real e mensurável (segurança, performance, manutenção).
4. **Recommendation:** ação específica e implementável. Referenciar o padrão do `refactoring-playbook.md` quando aplicável (ex: "Aplicar PT-02: Parâmetros Posicionais").
5. **Ordenação:** sempre CRITICAL primeiro, depois HIGH, MEDIUM e LOW.
6. **Total:** contar todos os findings, incluindo os de baixa severidade.
7. **Confirmação:** a linha `Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]` é OBRIGATÓRIA. Aguardar resposta explícita `y` antes de qualquer modificação de arquivo.
