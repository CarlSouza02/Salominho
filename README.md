# 🦁 Salominho

Jogo educativo de estudos bíblicos em **Python + Pygame**, com progressão por livros e capítulos da Bíblia.

## Versão atual

**v0.4.1 — Backgrounds temáticos do Pentateuco**

Esta versão consolida a estrutura de mundos, progresso persistente e os cinco primeiros mapas do Antigo Testamento.

### Estado atual

- **39 mundos** do Antigo Testamento cadastrados;
- **929 capítulos/fases** disponíveis na estrutura;
- progresso local em `save/progress.json`;
- estados de capítulo: **pendente**, **concluído** e **dominado**;
- seleção de mundos paginada;
- mapas roláveis;
- Gênesis 1 com leitura e quiz demonstrativos;
- sistema de áudio/vinheta;
- **Pentateuco funcional com 187 fases**:
  - Gênesis: 50;
  - Êxodo: 40;
  - Levítico: 27;
  - Números: 36;
  - Deuteronômio: 34.

## Direção visual dos mapas

A arquitetura definida para os mapas é:

```text
background pixel-art do livro
          +
trilha e capítulos desenhados pelo Python
          +
estado dinâmico do progresso
```

O **cenário artístico** deve ficar em um `background.png` próprio de cada livro.  
O Python/Pygame desenha por cima:

- caminho entre fases;
- número do capítulo;
- 🔴 capítulo pendente;
- 🔵 capítulo concluído;
- ⭐ capítulo dominado, quando aplicável.

Isso permite manter o mapa visualmente rico sem precisar gerar uma nova imagem sempre que o progresso do jogador mudar.

### Temas do Pentateuco

| Mundo | Tema visual |
|---|---|
| **Gênesis** | Criação e Éden → Queda/Caim/Noé → Babel/Patriarcas → José/Egito |
| **Êxodo** | Egito/opressão → Moisés → Pragas/Páscoa → Mar Vermelho → Deserto/maná → Sinai/Tabernáculo |
| **Levítico** | Tabernáculo, altar, tendas, sacerdócio e utensílios sagrados |
| **Números** | Deserto, grande acampamento, montanhas e peregrinação |
| **Deuteronômio** | Planícies de Moabe, Jordão, Canaã e Monte Nebo |

Os cinco primeiros mundos agora possuem **backgrounds temáticos em pixel art**, armazenados como `background.jpg` em cada pasta do Pentateuco. Os antigos `map_generated.png` e `map_preview.svg` foram removidos.

> A arte de fundo é fixa. A trilha, os capítulos e os estados 🔴/🔵/⭐ continuam sendo responsabilidade do Python/Pygame para que o progresso possa mudar sem regenerar a imagem.

## Estrutura principal

```text
Salominho/
├── main.py
├── VERSION
│
├── src/
│   ├── audio.py
│   ├── bible.py
│   ├── levels.py
│   ├── map_art.py
│   ├── map_layout.py
│   ├── pentateuch_maps.py
│   ├── progress.py
│   └── worlds.py
│
├── tools/
│   └── generate_pentateuch_maps.py
│
├── data/
│   ├── bible/
│   └── worlds/
│       └── old_testament.json
│
├── assets/
│   ├── audio/
│   ├── mascot/
│   └── worlds/
│       └── old_testament/
│           ├── 01_genesis/
│           ├── 02_exodo/
│           ├── 03_levitico/
│           ├── 04_numeros/
│           └── 05_deuteronomio/
│
├── save/
└── tests/
```

## Executar

Ubuntu/Debian:

```bash
sudo apt update
sudo apt install python3-pygame python3-requests python3-pil

git clone https://github.com/CarlSouza02/Salominho.git
cd Salominho
python3 main.py
```

Também é possível instalar as dependências listadas no projeto:

```bash
pip install -r requirements.txt
```

## Backgrounds atuais do Pentateuco

```text
assets/worlds/old_testament/01_genesis/background.jpg
assets/worlds/old_testament/02_exodo/background.jpg
assets/worlds/old_testament/03_levitico/background.jpg
assets/worlds/old_testament/04_numeros/background.jpg
assets/worlds/old_testament/05_deuteronomio/background.jpg
```

Esses arquivos são a base visual dos mundos. A integração deles no renderer do Pygame é o próximo passo da v0.4.x.

## Testes

```bash
python3 -m unittest discover -s tests -v
```

## Bíblia

A implementação atual usa uma consulta demonstrativa ao `bible-api.com` e cache local.

O fallback de Gênesis 1:1 utiliza a **Bíblia Livre (2018)**, de Diego Santos, Mario Sérgio e Marco Teles, disponibilizada pelo eBible sob licença **CC BY 4.0 Brasil**.

Para uma versão de produção, o plano é utilizar uma tradução licenciada/aberta armazenada localmente, preferencialmente em SQLite.

## Áudio

A vinheta de abertura é controlada por `src/audio.py`.

- WAV pode ser sintetizado localmente;
- existe MIDI editável no repositório;
- se `assets/audio/salominho_vinheta_v01.ogg` estiver presente, o jogo pode priorizar essa versão.

## Roadmap da v0.4.x

- [x] catálogo dos 39 livros do Antigo Testamento;
- [x] progresso persistente;
- [x] mapas roláveis;
- [x] Pentateuco com 187 fases;
- [x] gerador técnico em Python;
- [x] substituir os mapas técnicos por **backgrounds pixel-art temáticos**;
- [ ] integrar os backgrounds finais ao Pygame;
- [ ] manter bolinhas/trilha dinâmicas sobre a arte;
- [ ] preencher leitura, quiz e devocional por capítulo;
- [ ] Bíblia offline;
- [ ] sprites definitivos do Salominho;
- [ ] modo EBD/gincana.

## Histórico resumido

- **v0.1**: menu, Gênesis 1, quiz e XP.
- **v0.2**: vinheta e áudio.
- **v0.3**: 39 mundos, 929 capítulos e progresso persistente.
- **v0.4.0**: mapas do Pentateuco, 187 fases e definição da arquitetura visual final.
- **v0.4.1**: remoção dos mapas técnicos e inclusão dos cinco backgrounds temáticos do Pentateuco.
- **v0.4.2**: primeiras quatro fases narrativas de Gênesis conectadas ao Pygame.

## Fases narrativas jogáveis de Gênesis

A v0.4.2 conecta os arquivos JSON de `assets/worlds/old_testament/01_genesis/phases/` ao Pygame.

As primeiras histórias jogáveis são:

- **Criação e Queda**, Gênesis 1–3, selo Obediência;
- **Caim e Abel**, Gênesis 4, selo Sinceridade;
- **A Arca de Noé**, Gênesis 6–9, selo Fidelidade;
- **Torre de Babel**, Gênesis 11:1–9, selo Humildade.

Fluxo de cada fase:

```text
Mapa → Introdução → Narrativa → Quiz → Devocional → Recompensa
```

O progresso dessas histórias é salvo separadamente da leitura dos capítulos bíblicos. Assim, concluir uma história não marca automaticamente o texto bíblico como lido.
