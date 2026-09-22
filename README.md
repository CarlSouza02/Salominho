# 🦁 SalmoNela

**Um jogo de estudos bíblicos em pixel art, desenvolvido em Python com Pygame.**

O SalmoNela é um projeto de aplicativo gamificado para tornar a leitura e o estudo da Bíblia mais interativos. Inspirado em jogos de progressão por fases, ele combinará leitura, quizzes, desafios e um mascote que acompanha a evolução do jogador.

> **Status:** pré-desenvolvimento. O mascote e as funcionalidades descritas abaixo representam o conceito e o planejamento do projeto, não recursos já implementados.

## 🎮 Como vai funcionar

**Ler → Responder → Ganhar XP → Desbloquear fases → Evoluir**

Cada fase terá uma passagem bíblica, perguntas sobre a leitura e uma explicação das respostas. O objetivo é incentivar a compreensão do texto, e não apenas a memorização de curiosidades.

## 🦁 Conheça o Salmão

Nosso mascote é um pequeno leão escriba em **pixel art**, com túnica, pergaminho e bolsa de estudos. Ele reagirá ao progresso do jogador com animações e mensagens.

Animações planejadas: `idle` (respirar e piscar), `happy` (acerto), `wrong` (erro), `thinking` (pensando), `reading` (lendo), `walking` (mapa) e `level_up` (evolução).

## ✨ Funcionalidades planejadas

- **Campanha por fases:** jornadas temáticas, começando por Gênesis.
- **Bíblia integrada:** leitura por livro, capítulo e versículo, com referências nas perguntas.
- **Quizzes variados:** múltipla escolha, completar versículos, ordenar acontecimentos e identificar personagens.
- **Progressão:** experiência (XP), níveis, conquistas e missões diárias.
- **Mascote animado:** reações aos acertos, erros e conquistas.
- **Multijogador (futuro):** duelos entre amigos, ligas e torneios.

## 🗺️ Primeira jornada: Gênesis

| Fase | Tema |
| --- | --- |
| 1 | A Criação |
| 2 | Adão e Eva |
| 3 | Caim e Abel |
| 4 | Noé |
| 5 | Torre de Babel |
| 6 | Abraão |
| 7 | Isaque |
| 8 | Jacó |
| 9 | José |
| 10 | Desafio final de Gênesis |

## 🛠️ Tecnologias

- **Python:** lógica do jogo.
- **Pygame:** interface, animações, colisões e eventos.
- **PNG / sprite sheets:** arte e animação em pixel art.
- **Integração bíblica:** fonte de texto a definir, respeitando licenças de tradução e termos de uso.

Se o projeto avançar para contas, rankings e partidas online, a arquitetura do backend será definida em uma etapa posterior.

## 📁 Estrutura proposta

```text
salmonela/
├── assets/
│   └── salmao/
│       ├── idle/
│       ├── happy/
│       ├── wrong/
│       └── walking/
├── src/
│   ├── mascot.py
│   ├── levels.py
│   ├── quiz.py
│   └── bible.py
├── data/
│   └── levels/
├── main.py
├── requirements.txt
└── README.md
```

> A estrutura acima é uma proposta para organizar os arquivos à medida que forem criados.

## 🚀 Como executar (quando o protótipo estiver disponível)

Pré-requisito: Python 3.11 ou superior.

```bash
git clone https://github.com/SEU-USUARIO/salmonela.git
cd salmonela
python -m pip install pygame
python main.py
```

Substitua `SEU-USUARIO` pelo seu nome de usuário do GitHub. O comando `python main.py` funcionará quando a primeira versão do jogo for adicionada ao repositório.

## 📌 Roadmap

- [ ] Definir o sprite do Salmão com fundo transparente.
- [ ] Criar animações básicas: parado, feliz e triste.
- [ ] Implementar a tela inicial com Pygame.
- [ ] Criar a primeira fase de Gênesis.
- [ ] Implementar perguntas, correção e feedback.
- [ ] Adicionar XP e desbloqueio de fases.
- [ ] Integrar uma tradução bíblica com permissão de uso.
- [ ] Adicionar missões e conquistas.
- [ ] Avaliar duelos e rankings online.

## 📖 Conteúdo bíblico e direitos autorais

As referências bíblicas poderão fazer parte dos desafios. A inclusão do texto integral de qualquer tradução dependerá de sua licença ou de autorização do detentor dos direitos. Não serão distribuídas traduções protegidas sem permissão.

## 🤝 Contribuições

O projeto está em fase inicial. Ideias sobre mecânicas, acessibilidade, arte em pixel art e conteúdo educativo são bem-vindas por meio das *Issues* do GitHub, quando o repositório estiver público.

---

**SalmoNela** • Estude. Evolua. Desafie.
