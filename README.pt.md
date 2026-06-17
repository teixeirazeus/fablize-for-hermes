<p align="center">
  <a href="README.md">English</a> ·
  <a href="README.zh.md">简体中文</a> ·
  <a href="README.pt.md"><strong>Português (BR)</strong></a>
</p>

# fablize-for-hermes — execute como Fábula, no Hermes Agent
![Banner](banner.png)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

Uma adaptação do [fablize](https://github.com/fivetaku/fablize) para o ecossistema do
[Hermes Agent](https://hermes-agent.nousresearch.com/). Este projeto transpõe os
procedimentos verificados do fablize — grounding de verificação, gate de evidência
multi-story, protocolo de investigação e prevenção de parada precoce — do sistema de
plugins do Claude Code para o sistema de skills do Hermes Agent.

**fablize** faz qualquer agente **levar uma tarefa até o fim — com evidência e
verificação — como procedimento, não como sorte.**

## A origem

O [fablize](https://github.com/fivetaku/fablize) nasceu de uma comparação controlada
entre Claude Opus e "Fable 5" (19 execuções A/B + 26 sessões reais, ~1.500 chamadas
de ferramenta). A descoberta: em tarefas fechadas com resposta definida (código,
lógica, builds) os dois modelos estavam virtualmente empatados. A diferença estava na
*profundidade* — seguir uma implicação um passo adiante — e isso se mostrou
**capacidade do modelo**, não algo injetável.

Mas o **procedimento** de um bom trabalho — executar de fato o que você constrói,
decompor tarefas multi-etapa com checkpoints de evidência, investigar bugs
sistematicamente — *isso sim é transferível*. O fablize entrega apenas os
procedimentos cujo efeito foi verificado.

## O que transfere e o que não transfere

| Traço | Transferível? | Como o fablize-for-hermes faz |
|---|---|---|
| Grounding de verificação (executar & observar o artefato) | ✅ | Seção 3 da skill — executar no renderizador real, observar saída, corrigir, re-executar |
| Completude multi-story + gate de evidência | ✅ | `scripts/goals.py` — decompor, checkpoint, recusar conclusão sem prova |
| Investigação sistemática (reproduzir → hipóteses → cadeia causal) | ✅ | Seção 2 da skill + `packs/investigation-protocol.txt` |
| Prevenção de parada precoce | ✅ | Regra fundamental da skill: sem promessas sem chamadas de ferramenta |
| Descoberta de defeitos fora do esperado | ❌ não possível | Capacidade — o modelo encontra, ou não |
| Detalhe criativo em aberto | ❌ não possível | Capacidade — só aparece onde não há resposta fixa |
| Profundidade de propagação autodirigida | ❌ não possível | Capacidade — propagação dirigida transfere; profundidade auto-iniciada não |

## O que está incluso

### 1. Skill do Hermes Agent (`skills/fablize/SKILL.md`)

O conjunto de regras comportamentais principal, estruturado como uma skill do Hermes
Agent (frontmatter YAML + markdown). Abrange:

- **Regras fundamentais** — sempre ativas: lidar com o resultado, fundamentar
  alegações em resultados de ferramentas, sem paradas precoces, confirmar ações
  destrutivas
- **Loop multi-story** — decompor tarefas com 2+ histórias → completar com
  evidência → gate de verificação na história final
- **Investigação profunda** — reproduzir → 3+ hipóteses concorrentes → rastrear
  cadeia causal → verificar antes/depois → relatar hipóteses rejeitadas
- **Grounding de verificação** — executar artefatos renderizáveis/executáveis,
  observar, corrigir, re-executar antes de declarar concluído
- **Teto de capacidade** — escalonar honestamente quando o limite do modelo é o
  bloqueio

### 2. Motor de metas (`scripts/goals.py`)

Um script Python autossuficiente (só stdlib) para decomposição multi-story com
gate de verificação. O estado persiste em `~/.hermes/fablize/` e sobrevive à morte
de sessão.

```bash
goals.py create --brief "Construir um dashboard" \
  --goal "design::Criar o layout HTML" \
  --goal "implement::Adicionar visualizações de gráfico" \
  --goal "verify::Executar e verificar se o dashboard renderiza corretamente"
goals.py next
# ... trabalhar esta história ...
goals.py checkpoint --id G001 --status complete --evidence "Layout criado com sidebar e painel principal"
goals.py status
```

### 3. Packs — arquivos de disciplina contextuais

- **`packs/verification-grounding-pack.txt`** — O loop de grounding: executar,
  observar, corrigir, re-executar. Para HTML, SVG, jogos, UI, gráficos, animações.
- **`packs/investigation-protocol.txt`** — O protocolo sistemático de debugging:
  reproduzir, hipóteses concorrentes, cadeia causal, verificar antes/depois.

### 4. Scripts de instalação (`setup/`)

- `setup.sh [--skill-only|--local|--global]` — Instala a skill no Hermes e
  opcionalmente injeta o bloco operacional em `AGENTS.md` ou `CLAUDE.md`
- `uninstall.sh [--skill-only|--local|--global|--all]` — Reverte a instalação

## Diferenças do fablize original

| Aspecto | fablize (original) | fablize-for-hermes |
|---|---|---|
| Plataforma | Plugin do Claude Code | Skill do Hermes Agent |
| Roteamento | Hook `UserPromptSubmit` via `hooks.json` | Conteúdo da skill — agente carrega e aplica a disciplina correspondente |
| Parada precoce | Hook Stop `finish-the-work.sh` (transcrição JSON) | Regra fundamental na skill — agente auto-implementa |
| Diretório de estado | `./.fablize/` (por projeto) | `~/.hermes/fablize/` (global do Hermes, sobrevive a sessões) |
| Scripts | Em `scripts/` — executados da raiz do repo | Mesmos scripts, adaptados para caminhos do Hermes |
| Instalação | Injeta em `CLAUDE.md` | Instala como skill do Hermes + opcionalmente injeta bloco |

## Instalação

### Instalação rápida (apenas skill)

```bash
git clone https://github.com/teixeirazeus/fablize-for-hermes.git
cd fablize-for-hermes
bash setup/setup.sh --skill-only
```

Em seguida, carregue a skill na sua sessão do Hermes:

```
skill_view(name='fablize')
```

### Instalação completa (skill + bloco sempre ativo)

```bash
bash setup/setup.sh --local    # injeta bloco em ./AGENTS.md
bash setup/setup.sh --global   # injeta bloco em ~/.claude/CLAUDE.md
```

### Desinstalação

```bash
bash setup/uninstall.sh --all
```

## Como se comporta

- **Gatilho:** carregue a skill `fablize`, ou ativação inline quando o agente
  detecta 2+ histórias, debugging ou artefatos renderizáveis
- **2+ histórias** → decomposição + gate de verificação via `goals.py`
- **Debugging** → protocolo de investigação (reproduzir → hipóteses → cadeia causal)
- **Artefato renderizável** → grounding de verificação (executar → observar →
  corrigir → re-executar)
- **Tarefa difícil** → pensamento adaptativo + escalonar para modelo mais forte
  se emperrar
- **Teto de capacidade** → escalonar honestamente (a armação não finge capacidade)

## Limitações honestas

- Não pode aumentar a capacidade do modelo. Qualidade criativa em aberto e descoberta
  autodirigida estão fora de alcance — isso é uma decisão de modelo, não de armação.
- Os números de efeito vêm da auto-medição do fablize original em ambiente
  familiar pequeno. A direção é sólida; os decimais não são assertivos.
- A regra de parada precoce depende de auto-implementação do agente, não de um hook
  determinístico. É uma diretriz, não uma garantia.

## Licença

MIT — mesma do fablize original. O fablize original por fivetaku é licenciado sob MIT.
Esta adaptação transpõe o design e os procedimentos para o ecossistema do Hermes Agent.
