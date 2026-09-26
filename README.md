# 🦁 Salominho | SalmoNela

Protótipo de jogo de estudos bíblicos em **Python + Pygame**.

## Versão 0.1

- Menu com o Salmão (imagem conceitual temporária).
- Mapa de Gênesis com dez fases esboçadas e uma acessível.
- Leitura de Gênesis 1:1–5 via `bible-api.com`, com cache local e fallback de 1 versículo.
- Quiz demonstrativo com 3 perguntas, explicações, resultados e XP.
- Projeto preparado para sprites transparentes e textos offline no futuro.

## Executar no Ubuntu/Debian

```bash
sudo apt update
sudo apt install python3-pygame python3-requests
git clone https://github.com/CarlSouza02/Salominho.git
cd Salominho
python3 main.py
```

No VS Code, selecione o interpretador `/usr/bin/python3` se o Pygame não for encontrado.

## Testes

```bash
python3 -m unittest discover -s tests -v
```

## Estrutura

```text
main.py                    telas e loop Pygame
src/bible.py               cliente bíblico, cache e fallback
src/levels.py              fases planejadas e quiz demonstrativo
assets/mascot/concept.png  miniatura conceitual (não é sprite transparente)
docs/ASSETS.md             especificações dos sprites e tiles
data/bible/README.md       plano de importação bíblica e créditos
tests/test_core.py         testes das funções de conteúdo
```

## Textos e licenças

A amostra offline de Gênesis 1:1 é da **Bíblia Livre (2018)** de Diego Santos, Mario Sérgio e Marco Teles, disponível em https://ebible.org/porbr2018/, sob licença **CC BY 4.0 Brasil**. O texto completo não está incluído.

O serviço `bible-api.com` é externo. Para o lançamento, a proposta é importar uma tradução aberta para SQLite.

## Roadmap

- [x] Menu em Pygame e mapa provisório
- [x] Uma fase com quiz e XP
- [x] Consulta bíblica demonstrativa com cache
- [ ] Criar sprites PNG transparentes e animações
- [ ] Desenhar tiles e mapa pixel art
- [ ] Integrar Bíblia offline em SQLite
- [ ] Desenvolver fases seguintes e salvar progresso
- [ ] Amigos, duelos e ranking
