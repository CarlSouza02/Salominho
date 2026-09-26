"""Salominho: protótipo desktop em Pygame. Execute: python3 main.py."""
from __future__ import annotations

import math
from pathlib import Path

import pygame

from src.bible import get_creation_passage
from src.levels import LEVELS, QUESTIONS

BASE = Path(__file__).resolve().parent
WIDTH, HEIGHT, FPS = 1024, 680, 60
INK = (50, 43, 42)
DARK = (48, 70, 66)
CREAM = (250, 244, 231)
PAPER = (255, 251, 242)
GOLD = (244, 188, 73)
GREEN = (79, 128, 93)
MUTED = (120, 112, 100)


def wrap_text(text: str, font: pygame.font.Font, max_width: int) -> list[str]:
    words, result, line = text.split(), [], ""
    for word in words:
        trial = (line + " " + word).strip()
        if line and font.size(trial)[0] > max_width:
            result.append(line)
            line = word
        else:
            line = trial
    if line:
        result.append(line)
    return result


class Game:
    def __init__(self, passage: dict):
        pygame.init()
        pygame.display.set_caption("Salominho | SalmoNela")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("dejavusans", 23)
        self.small = pygame.font.SysFont("dejavusans", 17)
        self.large = pygame.font.SysFont("dejavusans", 45, bold=True)
        self.bold = pygame.font.SysFont("dejavusans", 25, bold=True)
        self.passage = passage
        self.page = "home"
        self.xp = 0
        self.question_index = 0
        self.correct_count = 0
        self.answered = False
        self.selected = None
        self.buttons = []
        art = BASE / "assets" / "mascot" / "idle_01.png"
        if not art.exists():
            art = BASE / "assets" / "mascot" / "concept.png"
        try:
            self.mascot = pygame.image.load(str(art)).convert_alpha()
            self.mascot = pygame.transform.scale(self.mascot, (225, 225))
        except (pygame.error, FileNotFoundError):
            self.mascot = None

    def text(self, msg, x, y, color=INK, font=None):
        surf = (font or self.font).render(str(msg), True, color)
        self.screen.blit(surf, (x, y))

    def panel(self, rect, color=PAPER, radius=20):
        pygame.draw.rect(self.screen, color, rect, border_radius=radius)
        pygame.draw.rect(self.screen, (226, 211, 183), rect, 2, border_radius=radius)

    def button(self, title, rect, action, bg=GOLD):
        active = rect.collidepoint(pygame.mouse.get_pos())
        draw_bg = tuple(min(255, c + 9) for c in bg) if active else bg
        pygame.draw.rect(self.screen, draw_bg, rect, border_radius=13)
        pygame.draw.rect(self.screen, INK, rect, 2, border_radius=13)
        label = self.bold.render(title, True, INK)
        self.screen.blit(label, label.get_rect(center=rect.center))
        self.buttons.append((rect, action))

    def mascot_at(self, x, y):
        if self.mascot is not None:
            bob = int(4 * math.sin(pygame.time.get_ticks() / 480))
            self.screen.blit(self.mascot, (x, y + bob))
        else:
            pygame.draw.circle(self.screen, GOLD, (x + 110, y + 110), 100)
            self.text("Leão", x + 85, y + 105)

    def heading(self, title):
        self.text(title, 52, 35, INK, self.large)
        self.text(f"XP: {self.xp}", WIDTH - 162, 46, DARK, self.bold)

    def home(self):
        self.heading("Salominho")
        self.text("SalmoNela: estude, responda e evolua!", 55, 108)
        self.panel(pygame.Rect(54, 169, 916, 416))
        self.mascot_at(110, 243)
        self.text("Seu primeiro mundo: Gênesis", 438, 255, DARK, self.bold)
        self.text("Uma fase jogável, 3 perguntas e o Salmão.", 438, 305)
        self.button("JOGAR", pygame.Rect(455, 369, 370, 64), lambda: self.go("map"))
        self.button("LER A BÍBLIA", pygame.Rect(455, 464, 370, 64), lambda: self.go("read"), GREEN)
        self.text("Protótipo 0.1: mapa e animações definitivos virão depois.", 54, 607, MUTED, self.small)

    def world_map(self):
        self.heading("Mundo 1: Gênesis")
        self.text("Fase 1 liberada | As demais são previstas para versões futuras.", 55, 110, MUTED, self.small)
        self.panel(pygame.Rect(52, 156, 920, 442), (229, 238, 213))
        for idx, (title, _) in enumerate(LEVELS):
            col, row = idx % 5, idx // 5
            x, y = 145 + col * 180, 292 + row * 188
            pygame.draw.circle(self.screen, GOLD if idx == 0 else (169, 182, 162), (x, y), 42)
            pygame.draw.circle(self.screen, DARK, (x, y), 42, 3)
            self.text(str(idx + 1) if idx == 0 else "×", x - 8, y - 15, INK, self.bold)
            s = self.small.render(title, True, INK)
            self.screen.blit(s, s.get_rect(center=(x, y + 66)))
            if idx == 0:
                self.buttons.append((pygame.Rect(x - 42, y - 42, 84, 84), lambda: self.go("read")))
        self.button("VOLTAR", pygame.Rect(53, 614, 170, 46), lambda: self.go("home"), (235, 225, 203))

    def reading(self):
        self.heading("Fase 1: A Criação")
        self.panel(pygame.Rect(53, 118, 910, 474))
        self.text(self.passage["reference"], 78, 139, DARK, self.bold)
        y = 203
        for verse in self.passage["verses"][:5]:
            line = f'{verse["number"]}. {verse["text"]}'
            for subline in wrap_text(line, self.font, 815):
                if y > 475:
                    break
                self.text(subline, 79, y)
                y += 36
            y += 11
            if y > 475:
                break
        self.text(self.passage["translation"], 78, 531, MUTED, self.small)
        self.button("INICIAR QUIZ", pygame.Rect(545, 610, 390, 50), self.begin_quiz)
        self.button("MAPA", pygame.Rect(53, 610, 174, 50), lambda: self.go("map"), (235, 225, 203))

    def quiz(self):
        q = QUESTIONS[self.question_index]
        self.heading(f"Quiz {self.question_index + 1}/{len(QUESTIONS)}")
        self.panel(pygame.Rect(52, 125, 918, 478))
        self.text(q["prompt"], 76, 162, DARK, self.bold)
        for idx, option in enumerate(q["choices"]):
            rect = pygame.Rect(89, 228 + idx * 78, 830, 59)
            color = (235, 225, 203)
            if self.answered and idx == q["correct"]:
                color = (160, 222, 163)
            elif self.answered and idx == self.selected:
                color = (245, 163, 160)
            self.button(f"{chr(65 + idx)}) {option}", rect, lambda idx=idx: self.answer(idx), color)
        if self.answered:
            self.text(q["explanation"], 75, 563, DARK, self.small)
            self.button("PRÓXIMA", pygame.Rect(694, 617, 230, 45), self.next_question)

    def result(self):
        self.heading("Fase concluída!")
        self.panel(pygame.Rect(53, 139, 918, 446))
        self.mascot_at(125, 237)
        self.text(f"Acertos: {self.correct_count}/{len(QUESTIONS)}", 455, 264, DARK, self.bold)
        self.text(f"XP total: {self.xp}", 455, 324, DARK, self.bold)
        self.text("A próxima fase ficará disponível em outra versão.", 455, 389, MUTED, self.small)
        self.button("VOLTAR AO MAPA", pygame.Rect(456, 461, 414, 61), lambda: self.go("map"))

    def go(self, page):
        self.page = page

    def begin_quiz(self):
        self.question_index = 0
        self.correct_count = 0
        self.selected = None
        self.answered = False
        self.page = "quiz"

    def answer(self, index):
        if self.answered:
            return
        self.selected = index
        self.answered = True
        if index == QUESTIONS[self.question_index]["correct"]:
            self.correct_count += 1
            self.xp += 10

    def next_question(self):
        if not self.answered:
            return
        self.question_index += 1
        self.selected = None
        self.answered = False
        if self.question_index >= len(QUESTIONS):
            self.xp += 20
            self.page = "result"

    def run(self):
        while True:
            self.clock.tick(FPS)
            self.buttons = []
            self.screen.fill(CREAM)
            {
                "home": self.home,
                "map": self.world_map,
                "read": self.reading,
                "quiz": self.quiz,
                "result": self.result,
            }[self.page]()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.go("home")
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    for rect, action in reversed(self.buttons):
                        if rect.collidepoint(event.pos):
                            action()
                            break
            pygame.display.flip()


if __name__ == "__main__":
    passage = get_creation_passage()
    print("Fonte bíblica:", passage["translation"])
    if passage["offline"]:
        print("Sem rede: usando cache ou amostra de Gênesis 1:1.")
    Game(passage).run()
