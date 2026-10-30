"""Salominho: protótipo desktop em Pygame.

Fluxo atual:
Início -> seleção de mundo -> capítulos -> detalhe -> leitura/quiz.
"""
from __future__ import annotations

import math
from pathlib import Path

import pygame

from src.audio import play_intro
from src.bible import get_creation_passage
from src.levels import QUESTIONS
from src.map_art import draw_pentateuch_background
from src.map_layout import (
    build_path_segments,
    layout_chapter_nodes,
    path_segments,
    serpentine_nodes,
    world_height,
)
from src.pentateuch_maps import PENTATEUCH_IDS, PENTATEUCH_MAPS
from src.progress import Progress
from src.story_phases import GENESIS_PHASE_ANCHORS, load_genesis_story_phases
from src.worlds import load_old_testament, page_slice

BASE = Path(__file__).resolve().parent
WIDTH, HEIGHT, FPS = 1024, 680, 60

INK = (50, 43, 42)
DARK = (48, 70, 66)
CREAM = (250, 244, 231)
PAPER = (255, 251, 242)
GOLD = (244, 188, 73)
GREEN = (79, 128, 93)
BLUE = (74, 142, 210)
MUTED = (120, 112, 100)
LOCKED = (174, 170, 158)

GENESIS_LANDMARKS = {1: 0, 3: 1, 6: 2, 11: 3, 12: 4, 37: 5}

GENESIS_CHAPTERS = 50
GENESIS_MAP_VIEW = pygame.Rect(52, 126, 920, 468)
GENESIS_MAP_COLUMNS = 5
GENESIS_ROW_SPACING = 235
GENESIS_WORLD_HEIGHT = world_height(
    GENESIS_CHAPTERS,
    columns=GENESIS_MAP_COLUMNS,
    row_spacing=GENESIS_ROW_SPACING,
)
GENESIS_MAP_NODES = serpentine_nodes(
    GENESIS_CHAPTERS,
    world_width=GENESIS_MAP_VIEW.width,
    columns=GENESIS_MAP_COLUMNS,
    row_spacing=GENESIS_ROW_SPACING,
)
GENESIS_STAGE_LABELS = {
    1: "Criação",
    2: "Éden",
    3: "Queda",
    6: "Noé",
    11: "Babel",
    12: "Abraão",
    22: "Isaque",
    28: "Jacó",
    37: "José",
    50: "Fim",
}


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
    WORLDS_PER_PAGE = 12
    CHAPTERS_PER_PAGE = 20

    def __init__(self, passage: dict):
        pygame.init()
        pygame.display.set_caption("Salominho | Jornada Bíblica")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()

        self.font = pygame.font.SysFont("dejavusans", 23)
        self.small = pygame.font.SysFont("dejavusans", 17)
        self.tiny = pygame.font.SysFont("dejavusans", 14)
        self.large = pygame.font.SysFont("dejavusans", 42, bold=True)
        self.bold = pygame.font.SysFont("dejavusans", 24, bold=True)

        self.passage = passage
        self.worlds = load_old_testament(BASE)
        self.current_world = self.worlds[0]
        self.current_chapter = 1
        self.world_page = 0
        self.chapter_page = 0
        self.map_scroll = 0

        self.progress = Progress(BASE / "save" / "progress.json")
        self.story_phases = load_genesis_story_phases(BASE)
        self.current_story_phase = None
        self.story_segment_index = 0
        self.story_result_data = None
        self.page = "home"
        self.question_index = 0
        self.correct_count = 0
        self.answered = False
        self.selected = None
        self.buttons = []
        self.message = ""

        self.audio_on = play_intro(pygame, BASE)
        art = BASE / "assets" / "mascot" / "idle_01.png"
        if not art.exists():
            art = BASE / "assets" / "mascot" / "concept.png"
        try:
            self.mascot = pygame.image.load(str(art)).convert_alpha()
            self.mascot = pygame.transform.scale(self.mascot, (210, 210))
        except (pygame.error, FileNotFoundError):
            self.mascot = None

        # Primeiros sprites reais do Mundo Gênesis.
        self.genesis_sprites = []
        sheet_path = (
            BASE / "assets" / "worlds" / "old_testament" / "01_genesis"
            / "sprites" / "genesis_spritesheet.png"
        )
        if sheet_path.is_file():
            try:
                sheet = pygame.image.load(str(sheet_path)).convert_alpha()
                for index in range(6):
                    frame = sheet.subsurface(
                        pygame.Rect(index * 64, 0, 64, 64)
                    ).copy()
                    self.genesis_sprites.append(
                        pygame.transform.scale(frame, (40, 40))
                    )
            except pygame.error as exc:
                print(f"Não foi possível carregar os sprites de Gênesis: {exc}")

    @property
    def xp(self) -> int:
        return self.progress.xp

    def text(self, msg, x, y, color=INK, font=None):
        surf = (font or self.font).render(str(msg), True, color)
        self.screen.blit(surf, (x, y))

    def centered_text(self, msg, rect, color=INK, font=None):
        surf = (font or self.font).render(str(msg), True, color)
        self.screen.blit(surf, surf.get_rect(center=rect.center))

    def panel(self, rect, color=PAPER, radius=20):
        pygame.draw.rect(self.screen, color, rect, border_radius=radius)
        pygame.draw.rect(self.screen, (226, 211, 183), rect, 2, border_radius=radius)

    def button(self, title, rect, action, bg=GOLD, font=None):
        active = rect.collidepoint(pygame.mouse.get_pos())
        draw_bg = tuple(min(255, c + 9) for c in bg) if active else bg
        pygame.draw.rect(self.screen, draw_bg, rect, border_radius=13)
        pygame.draw.rect(self.screen, INK, rect, 2, border_radius=13)
        self.centered_text(title, rect, INK, font or self.bold)
        self.buttons.append((rect, action))

    def mascot_at(self, x, y, size=210):
        if self.mascot is not None:
            mascot = self.mascot
            if mascot.get_width() != size:
                mascot = pygame.transform.scale(self.mascot, (size, size))
            bob = int(4 * math.sin(pygame.time.get_ticks() / 480))
            self.screen.blit(mascot, (x, y + bob))
        else:
            pygame.draw.circle(self.screen, GOLD, (x + size // 2, y + size // 2), size // 2)
            self.text("Leão", x + size // 3, y + size // 2)

    def draw_book_background(self, world, rect):
        """Desenha um fundo procedural simples para o mapa do livro."""
        if world.id == "genesis":
            pygame.draw.rect(self.screen, (190, 229, 160), rect, border_radius=24)

            # Trilha principal de terra.
            pygame.draw.rect(
                self.screen,
                (218, 196, 145),
                pygame.Rect(rect.x + 60, rect.y + 180, rect.w - 120, 95),
                border_radius=48,
            )

            # Árvores decorativas.
            tree_positions = [
                (rect.x + 70, rect.y + 70),
                (rect.x + 180, rect.y + 40),
                (rect.x + 840, rect.y + 70),
                (rect.x + 780, rect.y + 350),
                (rect.x + 130, rect.y + 360),
            ]
            for tx, ty in tree_positions:
                pygame.draw.circle(self.screen, (41, 104, 58), (tx, ty), 26)
                pygame.draw.circle(self.screen, (57, 140, 77), (tx - 10, ty - 8), 20)
                pygame.draw.circle(self.screen, (57, 140, 77), (tx + 12, ty - 5), 18)
                pygame.draw.rect(
                    self.screen,
                    (109, 72, 42),
                    pygame.Rect(tx - 5, ty + 15, 10, 24),
                )

            # Rio decorativo.
            river = [
                (rect.x + 40, rect.y + 420),
                (rect.x + 180, rect.y + 390),
                (rect.x + 340, rect.y + 430),
                (rect.x + 540, rect.y + 405),
                (rect.x + 730, rect.y + 445),
                (rect.x + 900, rect.y + 420),
            ]
            pygame.draw.lines(self.screen, (80, 170, 235), False, river, 24)
            pygame.draw.lines(self.screen, (180, 235, 255), False, river, 8)
        else:
            pygame.draw.rect(self.screen, (218, 228, 208), rect, border_radius=24)

    def heading(self, title, subtitle=None):
        self.text(title, 48, 29, INK, self.large)
        self.text(f"XP: {self.xp}", WIDTH - 155, 39, DARK, self.bold)
        if subtitle:
            self.text(subtitle, 50, 82, MUTED, self.small)
        self.text("M: som " + ("ON" if self.audio_on else "OFF"), WIDTH - 173, 86, MUTED, self.small)

    def go(self, page):
        self.page = page
        self.message = ""

    # ------------------------------------------------------------------
    # TELAS
    # ------------------------------------------------------------------

    def home(self):
        self.heading("Salominho", "Jornada Bíblica")
        self.panel(pygame.Rect(48, 132, 928, 468))
        self.mascot_at(100, 235)

        self.text("Sua jornada pela Bíblia começa aqui.", 397, 222, DARK, self.bold)
        self.text("39 mundos do Antigo Testamento já cadastrados.", 397, 271)
        self.text("Cada livro é um mundo e cada capítulo é uma fase.", 397, 309, MUTED, self.small)

        self.button(
            "CONTINUAR EM GÊNESIS",
            pygame.Rect(414, 365, 440, 62),
            self.open_genesis,
            GREEN,
        )
        self.button(
            "SELECIONAR MUNDO",
            pygame.Rect(414, 452, 440, 62),
            lambda: self.go("world_select"),
            GOLD,
        )

        self.text(
            "Protótipo v0.4.2 • 4 fases narrativas de Gênesis",
            55, 626, MUTED, self.small
        )

    def world_select(self):
        visible, page, pages = page_slice(
            self.worlds, self.world_page, self.WORLDS_PER_PAGE
        )
        self.world_page = page
        self.heading(
            "Antigo Testamento",
            f"Escolha um mundo • página {page + 1}/{pages}"
        )

        cols = 4
        start_x, start_y = 55, 142
        card_w, card_h = 217, 118
        gap_x, gap_y = 21, 22

        for i, world in enumerate(visible):
            row, col = divmod(i, cols)
            x = start_x + col * (card_w + gap_x)
            y = start_y + row * (card_h + gap_y)
            rect = pygame.Rect(x, y, card_w, card_h)

            has_map = world.id in PENTATEUCH_IDS
            color = (228, 239, 219) if has_map else PAPER
            self.panel(rect, color, 14)
            self.text(f"{world.order:02d}", x + 13, y + 10, MUTED, self.tiny)
            self.text(world.name, x + 13, y + 33, DARK, self.bold)
            self.text(f"{world.chapters} capítulos", x + 13, y + 70, MUTED, self.small)
            self.text(
                "MAPA PRONTO" if has_map else "PLANEJADO",
                x + 13,
                y + 94,
                GREEN if has_map else MUTED,
                self.tiny,
            )
            self.buttons.append((rect, lambda w=world: self.open_world(w)))

        if page > 0:
            self.button("◀", pygame.Rect(55, 602, 75, 48), self.prev_world_page, PAPER)
        if page < pages - 1:
            self.button("▶", pygame.Rect(894, 602, 75, 48), self.next_world_page, PAPER)

        self.button("INÍCIO", pygame.Rect(419, 602, 185, 48), lambda: self.go("home"), PAPER)

    @property
    def map_config(self):
        return PENTATEUCH_MAPS.get(self.current_world.id)

    @property
    def max_map_scroll(self) -> int:
        config = self.map_config
        if config is None:
            return 0
        return max(0, config.world_height - GENESIS_MAP_VIEW.height)

    def set_map_scroll(self, value: int):
        self.map_scroll = max(0, min(int(value), self.max_map_scroll))

    def scroll_map(self, delta: int):
        self.set_map_scroll(self.map_scroll + delta)

    def visible_map_y(self, world_y: int) -> int:
        return GENESIS_MAP_VIEW.top + world_y - self.map_scroll

    def world_map(self):
        if self.current_world.id in PENTATEUCH_IDS:
            self.pentateuch_world_map()
        else:
            self.generic_world_map()

    def pentateuch_world_map(self):
        world = self.current_world
        config = PENTATEUCH_MAPS[world.id]
        read_count, mastered_count = self.progress.count_world(
            world.id, world.chapters
        )

        self.heading(
            f"Mundo {world.order}: {world.name}",
            (
                f"{world.chapters} capítulos = {world.chapters} fases • "
                f"lidos {read_count} • dominados {mastered_count}"
            ),
        )

        draw_pentateuch_background(
            self.screen,
            GENESIS_MAP_VIEW,
            self.map_scroll,
            config,
        )

        self.screen.set_clip(GENESIS_MAP_VIEW)

        for (ax, ay), (bx, by) in path_segments(config.nodes):
            a = (GENESIS_MAP_VIEW.left + ax, self.visible_map_y(ay))
            b = (GENESIS_MAP_VIEW.left + bx, self.visible_map_y(by))
            if (
                max(a[1], b[1]) < GENESIS_MAP_VIEW.top - 50
                or min(a[1], b[1]) > GENESIS_MAP_VIEW.bottom + 50
            ):
                continue
            pygame.draw.line(self.screen, (126, 94, 61), a, b, 13)
            pygame.draw.line(self.screen, (238, 213, 158), a, b, 7)

        for node in config.nodes:
            x = GENESIS_MAP_VIEW.left + node.x
            y = self.visible_map_y(node.y)

            if y < GENESIS_MAP_VIEW.top - 80 or y > GENESIS_MAP_VIEW.bottom + 80:
                continue

            state = self.progress.chapter(world.id, node.chapter)
            if state["mastered"]:
                fill = GOLD
            elif state["read"]:
                fill = BLUE
            else:
                fill = (238, 228, 204)

            hit = pygame.Rect(x - 31, y - 31, 62, 62)
            if hit.collidepoint(pygame.mouse.get_pos()):
                pygame.draw.circle(
                    self.screen, (255, 248, 205), (x, y), 38
                )

            pygame.draw.circle(self.screen, fill, (x, y), 31)
            pygame.draw.circle(self.screen, DARK, (x, y), 31, 3)

            label = self.small.render(str(node.chapter), True, INK)
            self.screen.blit(label, label.get_rect(center=(x, y)))

            if node.chapter in config.landmarks:
                tag = self.tiny.render(
                    config.landmarks[node.chapter], True, DARK
                )
                box = tag.get_rect(center=(x, y + 47))
                bg = box.inflate(12, 7)
                pygame.draw.rect(
                    self.screen, (255, 247, 225), bg, border_radius=6
                )
                pygame.draw.rect(
                    self.screen, config.accent, bg, 1, border_radius=6
                )
                self.screen.blit(tag, box)

            # Os sprites especiais existentes continuam aparecendo em Gênesis.
            if (
                world.id == "genesis"
                and node.chapter in GENESIS_LANDMARKS
                and self.genesis_sprites
            ):
                sprite_index = GENESIS_LANDMARKS[node.chapter]
                if sprite_index < len(self.genesis_sprites):
                    self.screen.blit(
                        self.genesis_sprites[sprite_index],
                        (x - 20, y - 78),
                    )

            self.buttons.append(
                (hit, lambda c=node.chapter: self.open_chapter(c))
            )

        self.screen.set_clip(None)

        pygame.draw.rect(
            self.screen, DARK, GENESIS_MAP_VIEW, 3, border_radius=22
        )

        track = pygame.Rect(
            980, GENESIS_MAP_VIEW.top, 10, GENESIS_MAP_VIEW.height
        )
        pygame.draw.rect(
            self.screen, (220, 211, 194), track, border_radius=5
        )
        ratio = GENESIS_MAP_VIEW.height / config.world_height
        thumb_h = max(38, int(GENESIS_MAP_VIEW.height * ratio))
        travel = GENESIS_MAP_VIEW.height - thumb_h
        pos_ratio = (
            self.map_scroll / self.max_map_scroll
            if self.max_map_scroll
            else 0
        )
        thumb = pygame.Rect(
            track.x,
            track.y + int(travel * pos_ratio),
            track.w,
            thumb_h,
        )
        pygame.draw.rect(
            self.screen, config.accent, thumb, border_radius=5
        )

        self.button(
            "MUNDOS",
            pygame.Rect(52, 610, 165, 48),
            lambda: self.go("world_select"),
            PAPER,
        )
        self.button(
            "▲",
            pygame.Rect(794, 610, 70, 48),
            lambda: self.scroll_map(-310),
            PAPER,
        )
        self.button(
            "▼",
            pygame.Rect(878, 610, 70, 48),
            lambda: self.scroll_map(310),
            PAPER,
        )

        self.text("○ não lido", 255, 620, MUTED, self.tiny)
        self.text("● lido", 355, 620, BLUE, self.tiny)
        self.text("★ dominado", 430, 620, GOLD, self.tiny)
        self.text(
            f"{world.chapters} capítulos no mapa",
            560,
            620,
            DARK,
            self.tiny,
        )

    def generic_world_map(self):
        world = self.current_world
        chapters = list(range(1, world.chapters + 1))
        visible, page, pages = page_slice(
            chapters, self.chapter_page, self.CHAPTERS_PER_PAGE
        )
        self.chapter_page = page
        read_count, mastered_count = self.progress.count_world(
            world.id, world.chapters
        )

        self.heading(
            f"Mundo {world.order}: {world.name}",
            f"{world.chapters} capítulos • lidos {read_count} • dominados {mastered_count}",
        )

        map_rect = pygame.Rect(42, 118, 940, 470)
        self.draw_book_background(world, map_rect)

        nodes = layout_chapter_nodes(
            visible,
            (map_rect.x, map_rect.y, map_rect.w, map_rect.h),
            cols=5,
        )

        # Caminho ligando as fases.
        for start_pos, end_pos in build_path_segments(nodes):
            pygame.draw.line(self.screen, (110, 90, 70), start_pos, end_pos, 8)
            pygame.draw.line(self.screen, (193, 170, 120), start_pos, end_pos, 4)

        # Bolinhas dos capítulos.
        for node in nodes:
            chapter = node["chapter"]
            x, y = node["x"], node["y"]
            state = self.progress.chapter(world.id, chapter)

            if state["mastered"]:
                fill = GOLD
            elif state["read"]:
                fill = BLUE
            else:
                fill = LOCKED

            pygame.draw.circle(self.screen, fill, (x, y), 28)
            pygame.draw.circle(self.screen, DARK, (x, y), 28, 3)

            label = self.small.render(str(chapter), True, INK)
            self.screen.blit(label, label.get_rect(center=(x, y)))

            if (
                world.id == "genesis"
                and chapter in GENESIS_LANDMARKS
                and self.genesis_sprites
            ):
                sprite_index = GENESIS_LANDMARKS[chapter]
                if sprite_index < len(self.genesis_sprites):
                    self.screen.blit(
                        self.genesis_sprites[sprite_index],
                        (x - 20, y - 72),
                    )

            hit = pygame.Rect(x - 30, y - 30, 60, 60)
            self.buttons.append((hit, lambda c=chapter: self.open_chapter(c)))

        if visible:
            self.text(
                f"Capítulos {visible[0]}–{visible[-1]}",
                438, 552, DARK, self.small
            )

        if page > 0:
            self.button(
                "◀",
                pygame.Rect(52, 608, 75, 45),
                self.prev_chapter_page,
                PAPER,
            )
        if page < pages - 1:
            self.button(
                "▶",
                pygame.Rect(897, 608, 75, 45),
                self.next_chapter_page,
                PAPER,
            )

        self.button(
            "MUNDOS",
            pygame.Rect(414, 608, 196, 45),
            lambda: self.go("world_select"),
            PAPER,
        )

        self.text("cinza = não lido", 145, 613, MUTED, self.tiny)
        self.text("azul = lido", 655, 613, BLUE, self.tiny)
        self.text("dourado = dominado", 745, 613, GOLD, self.tiny)

    def story_phase_for_current_chapter(self):
        if self.current_world.id != "genesis":
            return None
        phase_id = GENESIS_PHASE_ANCHORS.get(self.current_chapter)
        return self.story_phases.get(phase_id) if phase_id else None

    def chapter_detail(self):
        world = self.current_world
        chapter = self.current_chapter
        state = self.progress.chapter(world.id, chapter)
        story_phase = self.story_phase_for_current_chapter()

        self.heading(f"{world.name} {chapter}", "Detalhes da fase")
        self.panel(pygame.Rect(70, 145, 884, 420))

        self.text(f"Mundo: {world.name}", 118, 191, DARK, self.bold)
        self.text(f"Capítulo: {chapter}/{world.chapters}", 118, 231)

        status = "Dominado" if state["mastered"] else "Lido" if state["read"] else "Não iniciado"
        self.text(f"Leitura bíblica: {status}", 118, 272, DARK)

        if story_phase:
            phase_state = self.progress.phase(story_phase["id"])
            story_status = (
                "Dominada ★" if phase_state["mastered"]
                else "Concluída" if phase_state["completed"]
                else "Não iniciada"
            )
            self.text(
                f'História: {story_phase["title"]}',
                118, 315, GREEN, self.bold
            )
            self.text(
                f'{story_phase["bible_reference"]} • {story_status}',
                118, 350, MUTED, self.small
            )

            self.button(
                "JOGAR FASE",
                pygame.Rect(118, 405, 330, 62),
                self.begin_story_phase,
                GOLD,
            )
            if world.id == "genesis" and chapter == 1:
                self.button(
                    "LER GÊNESIS 1",
                    pygame.Rect(488, 405, 330, 62),
                    lambda: self.go("read"),
                    GREEN,
                )
            else:
                self.button(
                    "VOLTAR AO MAPA",
                    pygame.Rect(488, 405, 330, 62),
                    lambda: self.go("map"),
                    PAPER,
                )
        else:
            self.text(
                "Conteúdo desta fase será adicionado durante a produção do mundo.",
                118, 342, MUTED, self.small
            )
            self.button(
                "VOLTAR AO MAPA",
                pygame.Rect(340, 423, 345, 62),
                lambda: self.go("map"),
                PAPER,
            )

        if self.message:
            self.text(self.message, 118, 510, GREEN, self.small)

    def story_intro(self):
        phase = self.current_story_phase
        if not phase:
            self.go("map")
            return

        phase_state = self.progress.phase(phase["id"])
        self.heading(phase["title"], phase["bible_reference"])
        self.panel(pygame.Rect(64, 130, 896, 450))

        self.text("Objetivo", 105, 170, DARK, self.bold)
        y = 210
        for line in wrap_text(phase["objective"], self.font, 780):
            self.text(line, 105, y)
            y += 32

        self.text("Personagens", 105, y + 18, DARK, self.bold)
        self.text(", ".join(phase["characters"]), 105, y + 56, MUTED, self.small)

        reward = phase["reward"]["name"]
        status = (
            "Dominada ★" if phase_state["mastered"]
            else "Concluída" if phase_state["completed"]
            else "Nova fase"
        )
        self.text(f"Recompensa: selo {reward}", 105, 382, GREEN, self.bold)
        self.text(f"Status: {status}", 105, 421, MUTED, self.small)

        self.button(
            "COMEÇAR HISTÓRIA",
            pygame.Rect(535, 495, 360, 58),
            lambda: self.go("story_narration"),
            GOLD,
        )
        self.button(
            "MAPA",
            pygame.Rect(105, 495, 190, 58),
            lambda: self.go("map"),
            PAPER,
        )

    def story_narration(self):
        phase = self.current_story_phase
        parts = phase["narration"]
        index = self.story_segment_index
        text = parts[index]

        self.heading(
            phase["title"],
            f'História {index + 1}/{len(parts)} • {phase["bible_reference"]}',
        )
        self.panel(pygame.Rect(65, 135, 894, 430))

        self.text("Narrativa", 110, 177, DARK, self.bold)
        y = 230
        for line in wrap_text(text, self.font, 790):
            self.text(line, 110, y)
            y += 36

        event_index = min(index, len(phase["key_events"]) - 1)
        event = phase["key_events"][event_index]
        y = max(y + 24, 390)
        self.text("Ponto-chave", 110, y, GREEN, self.bold)
        y += 38
        for line in wrap_text(event, self.small, 790):
            self.text(line, 110, y, DARK, self.small)
            y += 27

        if index > 0:
            self.button(
                "◀ ANTERIOR",
                pygame.Rect(105, 595, 210, 48),
                self.prev_story_segment,
                PAPER,
                self.small,
            )

        label = "IR PARA O QUIZ" if index == len(parts) - 1 else "PRÓXIMO ▶"
        self.button(
            label,
            pygame.Rect(680, 595, 245, 48),
            self.next_story_segment,
            GOLD,
            self.small,
        )

    def story_quiz(self):
        phase = self.current_story_phase
        questions = phase["quiz"]
        q = questions[self.question_index]

        self.heading(
            f'Quiz {self.question_index + 1}/{len(questions)}',
            phase["title"],
        )
        self.panel(pygame.Rect(52, 125, 918, 478))

        y = 158
        for line in wrap_text(q["question"], self.bold, 830):
            self.text(line, 76, y, DARK, self.bold)
            y += 30

        option_y = max(225, y + 18)
        for idx, option in enumerate(q["options"]):
            rect = pygame.Rect(89, option_y + idx * 72, 830, 54)
            color = (235, 225, 203)
            if self.answered and idx == q["correct_index"]:
                color = (160, 222, 163)
            elif self.answered and idx == self.selected:
                color = (245, 163, 160)
            self.button(
                f"{chr(65 + idx)}) {option}",
                rect,
                lambda idx=idx: self.answer_story(idx),
                color,
                self.small,
            )

        if self.answered:
            ey = option_y + len(q["options"]) * 72 + 4
            for line in wrap_text(q["explanation"], self.small, 610):
                self.text(line, 76, ey, DARK, self.small)
                ey += 24
            self.button(
                "PRÓXIMA",
                pygame.Rect(720, 612, 205, 45),
                self.next_story_question,
                GOLD,
                self.small,
            )

    def story_devotional(self):
        phase = self.current_story_phase
        devotional = phase["devotional"]

        self.heading("Devocional", phase["title"])
        self.panel(pygame.Rect(70, 138, 884, 445))
        self.text(devotional["title"], 112, 184, DARK, self.bold)

        y = 235
        for line in wrap_text(devotional["text"], self.font, 790):
            self.text(line, 112, y)
            y += 34

        y += 22
        self.text("Para pensar", 112, y, GREEN, self.bold)
        y += 38
        for line in wrap_text(devotional["reflection_question"], self.small, 790):
            self.text(line, 112, y, DARK, self.small)
            y += 26

        self.button(
            "CONCLUIR FASE",
            pygame.Rect(605, 606, 300, 48),
            self.finish_story_phase,
            GREEN,
            self.small,
        )

    def story_result(self):
        phase = self.current_story_phase
        result = self.story_result_data or {}
        total = len(phase["quiz"])
        mastered = bool(result.get("mastered"))

        self.heading("Fase concluída!", phase["title"])
        self.panel(pygame.Rect(70, 145, 884, 420))
        self.mascot_at(112, 245, 180)

        self.text(
            f"Acertos: {self.correct_count}/{total}",
            390, 220, DARK, self.bold
        )
        self.text(
            f'Selo: {phase["reward"]["name"]}',
            390, 270, GOLD, self.bold
        )
        self.text(f"XP total: {self.xp}", 390, 320, DARK, self.bold)
        self.text(
            "Fase DOMINADA ★" if mastered else "Fase concluída. Tente novamente para dominar.",
            390, 370,
            GREEN if mastered else MUTED,
            self.bold if mastered else self.small,
        )
        self.button(
            "VOLTAR AO MAPA",
            pygame.Rect(390, 445, 360, 58),
            lambda: self.go("map"),
            PAPER,
        )

    def reading(self):
        self.heading("Gênesis 1", "Leitura demonstrativa")
        self.panel(pygame.Rect(53, 118, 910, 474))
        self.text(self.passage["reference"], 78, 139, DARK, self.bold)

        y = 198
        for verse in self.passage["verses"][:5]:
            line = f'{verse["number"]}. {verse["text"]}'
            for subline in wrap_text(line, self.font, 815):
                if y > 440:
                    break
                self.text(subline, 79, y)
                y += 34
            y += 9
            if y > 440:
                break

        self.text(self.passage["translation"], 78, 500, MUTED, self.small)
        self.text("Protótipo: a versão final exibirá o capítulo completo.", 78, 530, MUTED, self.tiny)

        self.button("CONCLUIR LEITURA", pygame.Rect(535, 610, 405, 48), self.finish_reading, GREEN)
        self.button("MAPA", pygame.Rect(53, 610, 174, 48), lambda: self.go("map"), PAPER)

    def quiz(self):
        q = QUESTIONS[self.question_index]
        self.heading(f"Quiz {self.question_index + 1}/{len(QUESTIONS)}", "Gênesis 1")
        self.panel(pygame.Rect(52, 125, 918, 478))
        self.text(q["prompt"], 76, 162, DARK, self.bold)

        for idx, option in enumerate(q["choices"]):
            rect = pygame.Rect(89, 228 + idx * 78, 830, 59)
            color = (235, 225, 203)
            if self.answered and idx == q["correct"]:
                color = (160, 222, 163)
            elif self.answered and idx == self.selected:
                color = (245, 163, 160)
            self.button(
                f"{chr(65 + idx)}) {option}",
                rect,
                lambda idx=idx: self.answer(idx),
                color,
            )

        if self.answered:
            self.text(q["explanation"], 75, 563, DARK, self.small)
            self.button("PRÓXIMA", pygame.Rect(694, 617, 230, 45), self.next_question)

    def result(self):
        mastered = self.correct_count == len(QUESTIONS)
        self.heading("Fase concluída!", "Gênesis 1")
        self.panel(pygame.Rect(53, 139, 918, 446))
        self.mascot_at(116, 242, 190)

        self.text(f"Acertos: {self.correct_count}/{len(QUESTIONS)}", 421, 242, DARK, self.bold)
        self.text(f"XP total: {self.xp}", 421, 292, DARK, self.bold)
        self.text(
            "Capítulo DOMINADO ★" if mastered else "Tente novamente para dominar o capítulo.",
            421, 349,
            GREEN if mastered else MUTED,
            self.bold if mastered else self.small,
        )
        self.button("VOLTAR AO MAPA", pygame.Rect(421, 421, 390, 61), lambda: self.go("map"))

    def devotional_screen(self):
        self.heading("Devocional", "Gênesis 1")
        self.panel(pygame.Rect(72, 145, 880, 423))
        self.text("Criados com propósito", 118, 192, DARK, self.bold)
        lines = [
            "A criação nos lembra que a vida não é um acidente.",
            "O texto começa apresentando Deus como Criador e origem de tudo.",
            "Observe hoje algo da criação e agradeça conscientemente por isso.",
        ]
        y = 252
        for line in lines:
            for wrapped in wrap_text(line, self.font, 760):
                self.text(wrapped, 118, y)
                y += 38
            y += 8
        self.text("Devocional demonstrativo original do Salominho.", 118, 485, MUTED, self.small)
        self.button("VOLTAR", pygame.Rect(392, 599, 240, 50), lambda: self.go("chapter"), PAPER)

    # ------------------------------------------------------------------
    # AÇÕES
    # ------------------------------------------------------------------

    def begin_story_phase(self):
        phase = self.story_phase_for_current_chapter()
        if not phase:
            return
        self.current_story_phase = phase
        self.story_segment_index = 0
        self.question_index = 0
        self.correct_count = 0
        self.selected = None
        self.answered = False
        self.story_result_data = None
        self.go("story_intro")

    def prev_story_segment(self):
        self.story_segment_index = max(0, self.story_segment_index - 1)

    def next_story_segment(self):
        phase = self.current_story_phase
        if self.story_segment_index < len(phase["narration"]) - 1:
            self.story_segment_index += 1
        else:
            self.question_index = 0
            self.correct_count = 0
            self.selected = None
            self.answered = False
            self.go("story_quiz")

    def answer_story(self, index):
        if self.answered:
            return
        self.selected = index
        self.answered = True
        question = self.current_story_phase["quiz"][self.question_index]
        if index == question["correct_index"]:
            self.correct_count += 1

    def next_story_question(self):
        if not self.answered:
            return
        self.question_index += 1
        self.selected = None
        self.answered = False
        if self.question_index >= len(self.current_story_phase["quiz"]):
            self.go("story_devotional")

    def finish_story_phase(self):
        phase = self.current_story_phase
        self.story_result_data = self.progress.record_story_phase(
            phase["id"],
            self.correct_count,
            len(phase["quiz"]),
        )
        self.go("story_result")

    def open_genesis(self):
        self.open_world(self.worlds[0])

    def open_world(self, world):
        self.current_world = world
        self.chapter_page = 0
        self.map_scroll = 0
        self.go("map")

    def open_chapter(self, chapter):
        self.current_chapter = chapter
        self.go("chapter")

    def prev_world_page(self):
        self.world_page = max(0, self.world_page - 1)

    def next_world_page(self):
        self.world_page += 1

    def prev_chapter_page(self):
        self.chapter_page = max(0, self.chapter_page - 1)

    def next_chapter_page(self):
        self.chapter_page += 1

    def finish_reading(self):
        first = self.progress.mark_read("genesis", 1, 20)
        self.message = "+20 XP • capítulo marcado como lido" if first else "Capítulo já estava marcado como lido"
        self.current_world = self.worlds[0]
        self.current_chapter = 1
        self.go("chapter")
        self.message = "+20 XP • capítulo marcado como lido" if first else "Capítulo já estava marcado como lido"

    def devotional(self):
        self.go("devotional")

    def begin_quiz(self):
        self.current_world = self.worlds[0]
        self.current_chapter = 1
        self.question_index = 0
        self.correct_count = 0
        self.selected = None
        self.answered = False
        self.go("quiz")

    def answer(self, index):
        if self.answered:
            return
        self.selected = index
        self.answered = True
        if index == QUESTIONS[self.question_index]["correct"]:
            self.correct_count += 1

    def next_question(self):
        if not self.answered:
            return
        self.question_index += 1
        self.selected = None
        self.answered = False

        if self.question_index >= len(QUESTIONS):
            self.progress.record_quiz(
                "genesis",
                1,
                self.correct_count,
                len(QUESTIONS),
                xp_per_correct=10,
                mastery_bonus=20,
            )
            self.go("result")

    # ------------------------------------------------------------------
    # LOOP
    # ------------------------------------------------------------------

    def run(self):
        screens = {
            "home": self.home,
            "world_select": self.world_select,
            "map": self.world_map,
            "chapter": self.chapter_detail,
            "story_intro": self.story_intro,
            "story_narration": self.story_narration,
            "story_quiz": self.story_quiz,
            "story_devotional": self.story_devotional,
            "story_result": self.story_result,
            "read": self.reading,
            "quiz": self.quiz,
            "result": self.result,
            "devotional": self.devotional_screen,
        }

        while True:
            self.clock.tick(FPS)
            self.buttons = []
            self.screen.fill(CREAM)
            screens[self.page]()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return

                if event.type == pygame.KEYDOWN and event.key == pygame.K_m:
                    if pygame.mixer.get_init():
                        self.audio_on = not self.audio_on
                        if self.audio_on:
                            play_intro(pygame, BASE)
                        else:
                            pygame.mixer.music.stop()

                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    if self.page == "home":
                        pygame.quit()
                        return
                    self.go("home")

                if (
                    event.type == pygame.KEYDOWN
                    and self.page == "map"
                    and self.current_world.id in PENTATEUCH_IDS
                ):
                    if event.key in (
                        pygame.K_DOWN,
                        pygame.K_s,
                        pygame.K_PAGEDOWN,
                    ):
                        self.scroll_map(180)
                    elif event.key in (
                        pygame.K_UP,
                        pygame.K_w,
                        pygame.K_PAGEUP,
                    ):
                        self.scroll_map(-180)
                    elif event.key == pygame.K_HOME:
                        self.set_map_scroll(0)
                    elif event.key == pygame.K_END:
                        self.set_map_scroll(self.max_map_scroll)

                if (
                    event.type == pygame.MOUSEWHEEL
                    and self.page == "map"
                    and self.current_world.id in PENTATEUCH_IDS
                ):
                    self.scroll_map(-event.y * 150)

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
