import random
import numpy as np
import pygame
import sys
from collections import deque

# Inicialização do Pygame
pygame.init()
pygame.font.init()

# Constantes
TAMANHO_TILE = 100
PAINEL_LARGURA = 400
GRID_OFFSET_X, GRID_OFFSET_Y = 50, 50
FPS = 60

# Cores
PRETO = (0, 0, 0)
BRANCO = (255, 255, 255)
CINZA = (128, 128, 128)
CINZA_ESCURO = (64, 64, 64)
VERMELHO = (255, 0, 0)
VERDE = (0, 255, 0)
AZUL = (0, 0, 255)
AMARELO = (255, 255, 0)
ROXO = (128, 0, 128)

# Direções
Direcao = ["N", "S", "L", "O"]
Movimento = {"N": (-1, 0), "S": (1, 0), "L": (0, 1), "O": (0, -1)}

# Configuração da tela
#Cálculo de tamanho do Grid
GRID_SIZE = 4
LARGURA = GRID_OFFSET_X * 2 + TAMANHO_TILE * GRID_SIZE + PAINEL_LARGURA
ALTURA = GRID_OFFSET_Y * 2 + TAMANHO_TILE * GRID_SIZE

tela_cheia = False
screen = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Mundo de Wumpus")
clock = pygame.time.Clock()

# Definindo a tela cheia
info_monitor = pygame.display.Info()
MONITOR_LARGURA = info_monitor.current_w
MONITOR_ALTURA = info_monitor.current_h

# Fontes
fonte_pequena = pygame.font.SysFont('Helvetica', 16)
fonte_media = pygame.font.SysFont('Helvetica', 24)
fonte_grande = pygame.font.SysFont('Helvetica', 32)

class Mundo:
    def __init__(self):
        self.tamanho = 4
        self.mapa = np.full((self.tamanho, self.tamanho), "", dtype=object)
        self.visao = np.full((self.tamanho, self.tamanho), "", dtype=object)
        self.celulas_visitadas = np.zeros((self.tamanho, self.tamanho), dtype=bool)
        self.jogador = (0, 0)
        self.direcao = "L"
        self.flecha = True
        self.ouro = False
        self.ouroPego = False
        self.Wumpusvivo = True
        self.pontos = 0
        self.grito = False
        self.morto = False
        self.venceu = False
        self.mensagem = "Bem-vindo ao Mundo de Wumpus!"
        
        self.DisporMapa()
        self.celulas_visitadas[0][0] = True

    def DisporMapa(self):
        self.WumpusPos = self.RandPos(Ocupado=[(0, 0)])
        self.AdicionarPercepcao(self.WumpusPos, "Fedor", Adjacencia=True)
        self.mapa[self.WumpusPos[0]][self.WumpusPos[1]] = "W"

        self.abismos = []
        for i in range(3):
            AbismoPos = self.RandPos(Ocupado=[self.WumpusPos, (0, 0)] + self.abismos)
            self.abismos.append(AbismoPos)
            self.AdicionarPercepcao(AbismoPos, "Brisa", Adjacencia=True)
            self.mapa[AbismoPos[0]][AbismoPos[1]] += "A"

        self.OuroPos = self.RandPos(Ocupado=[self.WumpusPos, (0, 0)] + self.abismos)
        self.AdicionarPercepcao(self.OuroPos, "Brilho")
        self.mapa[self.OuroPos[0]][self.OuroPos[1]] = "O"

    def RandPos(self, Ocupado):
        while True:
            Posicao = [random.randint(0, self.tamanho - 1), random.randint(0, self.tamanho - 1)]
            if tuple(Posicao) not in [tuple(pos) for pos in Ocupado]:
                return tuple(Posicao)

    def AdicionarPercepcao(self, Posicao, Percepcao, Adjacencia=False):
        if Adjacencia:
            for direcaoX, direcaoY in Movimento.values():
                x, y = Posicao[0] + direcaoX, Posicao[1] + direcaoY
                if 0 <= x < self.tamanho and 0 <= y < self.tamanho:
                    if isinstance(self.visao[x][y], str):
                        if self.visao[x][y]:
                            self.visao[x][y] += f", {Percepcao}"
                        else:
                            self.visao[x][y] = Percepcao
        else:
            if isinstance(self.visao[Posicao[0]][Posicao[1]], str):
                if self.visao[Posicao[0]][Posicao[1]]:
                    self.visao[Posicao[0]][Posicao[1]] += f", {Percepcao}"
                else:
                    self.visao[Posicao[0]][Posicao[1]] = Percepcao

    def DirecaoJogador(self, NovaDirecao):
        self.direcao = NovaDirecao
        self.mensagem = f"Você virou para {self.direcao}"

    def MoverJogador(self):
        direcaoX, direcaoY = Movimento[self.direcao]
        novoX, novoY = self.jogador[0] + direcaoX, self.jogador[1] + direcaoY

        if 0 <= novoX < self.tamanho and 0 <= novoY < self.tamanho:
            self.jogador = (novoX, novoY)
            self.celulas_visitadas[novoX][novoY] = True
            Conteudo = self.mapa[novoX][novoY]
            if "W" in Conteudo and self.Wumpusvivo:
                self.morto = True
                self.pontos -= 100
                self.mensagem = "Você foi comido pelo Wumpus!"
            elif "A" in Conteudo:
                self.morto = True
                self.pontos -= 100
                self.mensagem = "Você caiu em um abismo!"
            elif "O" in Conteudo and not self.ouroPego:
                self.ouro = True
                self.mensagem = "Você encontrou o ouro!"
            else:
                self.pontos -= 1
                self.mensagem = "Você se moveu para uma nova posição."
        else:
            self.mensagem = "Ai! Você bateu em uma parede!"
            self.pontos -= 1

    def AtirarFlecha(self):
        if self.flecha:
            self.flecha = False
            self.pontos -= 10
            x, y = self.jogador
            atingiu_algo = False
            
            while not atingiu_algo:
                x += Movimento[self.direcao][0]
                y += Movimento[self.direcao][1]
                
                if 0 <= x < self.tamanho and 0 <= y < self.tamanho:
                    if (x, y) == self.WumpusPos and self.Wumpusvivo:
                        self.Wumpusvivo = False
                        self.grito = True
                        self.mapa[x][y] = ""
                        self.mensagem = "Você acertou o Wumpus!"
                        atingiu_algo = True
                    elif (x, y) in self.abismos:
                        self.mensagem = "Sua flecha caiu em um abismo!"
                        atingiu_algo = True
                else:
                    self.mensagem = "Sua flecha atingiu a parede!"
                    atingiu_algo = True
                    
            if not atingiu_algo:
                self.mensagem = "Você atirou a flecha... mas não acertou nada!"
        else:
            self.mensagem = "Você não tem mais flechas!"
            return False
        
    def PegarOuro(self):
        if self.jogador == self.OuroPos and self.ouro == True:
            self.ouroPego = True
            self.ouro = False
            self.mapa[self.OuroPos[0]][self.OuroPos[1]] = ""
            self.mensagem = "Você pegou o ouro!"
        else:
            self.mensagem = "Não há ouro aqui!"
        
    def Escalar(self):
        if self.jogador == (0, 0):
            if self.ouroPego:
                self.pontos += 1000
                self.venceu = True
                self.mensagem = f"Você ganhou! Pontuação: {self.pontos}"
            else:
                self.venceu = True
                self.mensagem = f"Você escapou sem o ouro. Pontuação: {self.pontos}"
        else:
            self.mensagem = "Você não pode escalar aqui!"

    def desenhar(self, screen):
        # Desenhar grid
        for i in range(self.tamanho):
            for j in range(self.tamanho):
                rect = pygame.Rect(GRID_OFFSET_X + j * TAMANHO_TILE, 
                                  GRID_OFFSET_Y + i * TAMANHO_TILE, 
                                  TAMANHO_TILE, TAMANHO_TILE)
                
                # Célula não visitada
                if not self.celulas_visitadas[i][j]:
                    pygame.draw.rect(screen, CINZA_ESCURO, rect)
                    pygame.draw.rect(screen, BRANCO, rect, 1)
                # Célula visitada
                else:
                    pygame.draw.rect(screen, CINZA, rect)
                    pygame.draw.rect(screen, BRANCO, rect, 1)
                    
                    # Desenhar conteúdo da célula
                    conteudo = self.mapa[i][j]
                    if conteudo:
                        if "W" in conteudo and self.Wumpusvivo:
                            # Desenhar Wumpus
                            texto = fonte_grande.render("W", True, VERMELHO)
                            screen.blit(texto, (rect.centerx - texto.get_width() // 2, 
                                              rect.centery - texto.get_height() // 2))
                        if "A" in conteudo:
                            # Desenhar Abismo
                            texto = fonte_grande.render("A", True, PRETO)
                            screen.blit(texto, (rect.centerx - texto.get_width() // 2, 
                                              rect.centery - texto.get_height() // 2))
                        if "O" in conteudo:
                            # Desenhar Ouro
                            texto = fonte_grande.render("O", True, AMARELO)
                            screen.blit(texto, (rect.centerx - texto.get_width() // 2, 
                                              rect.centery - texto.get_height() // 2))
                
                # Desenhar percepções
                if self.celulas_visitadas[i][j] and self.visao[i][j]:
                    percepcoes = self.visao[i][j].split(", ")
                    for idx, perc in enumerate(percepcoes):
                        if perc == "Fedor":
                            cor = VERMELHO
                        elif perc == "Brisa":
                            cor = AZUL
                        elif perc == "Brilho":
                            cor = AMARELO
                        else:
                            cor = BRANCO
                        
                        texto = fonte_pequena.render(perc, True, cor)
                        screen.blit(texto, (rect.x + 5, rect.y + 5 + idx * 20))
        
        # Desenhar o jogador
        i, j = self.jogador
        jogador_rect = pygame.Rect(GRID_OFFSET_X + j * TAMANHO_TILE, 
                                 GRID_OFFSET_Y + i * TAMANHO_TILE, 
                                 TAMANHO_TILE, TAMANHO_TILE)
        
        # Desenhar seta de direção
        if self.direcao == "N":
            pontos = [(jogador_rect.centerx, jogador_rect.y + 10),
                      (jogador_rect.centerx - 10, jogador_rect.centery),
                      (jogador_rect.centerx + 10, jogador_rect.centery)]
        elif self.direcao == "S":
            pontos = [(jogador_rect.centerx, jogador_rect.bottom - 10),
                      (jogador_rect.centerx - 10, jogador_rect.centery),
                      (jogador_rect.centerx + 10, jogador_rect.centery)]
        elif self.direcao == "L":
            pontos = [(jogador_rect.right - 10, jogador_rect.centery),
                      (jogador_rect.centerx, jogador_rect.centery - 10),
                      (jogador_rect.centerx, jogador_rect.centery + 10)]
        elif self.direcao == "O":
            pontos = [(jogador_rect.x + 10, jogador_rect.centery),
                      (jogador_rect.centerx, jogador_rect.centery - 10),
                      (jogador_rect.centerx, jogador_rect.centery + 10)]
        
        pygame.draw.polygon(screen, VERDE, pontos)
        
        # Desenhar informações do jogo
        info_x = GRID_OFFSET_X + self.tamanho * TAMANHO_TILE + 20
        info_y = GRID_OFFSET_Y
        
        # Título
        titulo = fonte_grande.render("Mundo de Wumpus", True, BRANCO)
        screen.blit(titulo, (info_x, info_y))
        info_y += 50
        
        # Pontuação
        pontos_texto = fonte_media.render(f"Pontuação: {self.pontos}", True, BRANCO)
        screen.blit(pontos_texto, (info_x, info_y))
        info_y += 30
        
        # Status da flecha
        if self.flecha:
            flecha_texto = fonte_media.render("Flecha: Disponível", True, VERDE)
        else:
            flecha_texto = fonte_media.render("Flecha: Usada", True, VERMELHO)
        screen.blit(flecha_texto, (info_x, info_y))
        info_y += 30
        
        # Status do ouro
        if self.ouroPego:
            ouro_texto = fonte_media.render("Ouro: Coletado", True, AMARELO)
        else:
            ouro_texto = fonte_media.render("Ouro: Não coletado", True, BRANCO)
        screen.blit(ouro_texto, (info_x, info_y))
        info_y += 30
        
        # Grito do Wumpus
        if self.grito:
            grito_texto = fonte_media.render("Você ouviu um grito!", True, VERMELHO)
            screen.blit(grito_texto, (info_x, info_y))
            info_y += 30
            self.grito = False
        
        # Mensagem
        mensagem_texto = fonte_media.render(self.mensagem, True, BRANCO)
        screen.blit(mensagem_texto, (info_x, info_y))
        info_y += 40
        
        # Instruções
        info_y += 20
        instrucoes = [
            "Controles:",
            "Setas - Move o jogador na direção pressionada",
            "F - Atirar flecha",
            "Espaço - Pegar Ouro ou Escalar",
            "ESC - Sair"
        ]
        
        for instrucao in instrucoes:
            texto = fonte_pequena.render(instrucao, True, BRANCO)
            screen.blit(texto, (info_x, info_y))
            info_y += 20
        
        # Tela de fim de jogo
        if self.morto or self.venceu:
            overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))
            
            if self.morto:
                texto = fonte_grande.render("Você morreu", True, VERMELHO)
            else:
                texto = fonte_grande.render("Você venceu!", True, VERDE)
            
            screen.blit(texto, (LARGURA // 2 - texto.get_width() // 2, 
                               ALTURA // 2 - texto.get_height() // 2))
            
            pontos_texto = fonte_media.render(f"Pontuação Final: {self.pontos}", True, BRANCO)
            screen.blit(pontos_texto, (LARGURA // 2 - pontos_texto.get_width() // 2, 
                                      ALTURA // 2 + 50))
            
            reiniciar_texto = fonte_media.render("Pressione R para reiniciar ou Q para sair", True, BRANCO)
            screen.blit(reiniciar_texto, (LARGURA // 2 - reiniciar_texto.get_width() // 2, 
                                        ALTURA // 2 + 100))

def bfs_wumpus(mundo):
    """
    Agente prioriza pegar o ouro evitando o Wumpus. Só tenta matar o Wumpus se não houver caminho seguro até o ouro.
    """
    tamanho = mundo.tamanho
    start = (0, 0)
    ouro = mundo.OuroPos
    saida = (0, 0)
    abismos = set(mundo.abismos)
    wumpus = mundo.WumpusPos if mundo.Wumpusvivo else None

    def adjacente_wumpus(pos):
        if not wumpus:
            return False
        for d in Movimento.values():
            nx, ny = pos[0] + d[0], pos[1] + d[1]
            if (nx, ny) == wumpus:
                return True
        return False

    def bfs_evitar_wumpus(start, goal):
        queue = deque()
        queue.append((start, [start]))
        visited = set()
        visited.add(start)
        while queue:
            pos, path = queue.popleft()
            if pos == goal:
                return path
            for d in Movimento.values():
                nx, ny = pos[0] + d[0], pos[1] + d[1]
                npos = (nx, ny)
                if 0 <= nx < tamanho and 0 <= ny < tamanho and npos not in abismos and npos not in visited:
                    if wumpus and npos == wumpus:
                        continue
                    visited.add(npos)
                    queue.append((npos, path + [npos]))
        return []

    actions = []
    pos = start
    direcao = 'L'
    flecha_usada = not mundo.flecha
    wumpus_morto = not mundo.Wumpusvivo

    # 1. Tenta caminho seguro até o ouro evitando o Wumpus
    path_to_ouro = bfs_evitar_wumpus(pos, ouro)
    if path_to_ouro:
        # Caminho seguro existe, só pega o ouro e volta
        for step in path_to_ouro[1:]:
            nova_dir = get_dir(pos, step)
            if direcao != nova_dir:
                actions.append(('virar', nova_dir))
                direcao = nova_dir
            actions.append(('mover', nova_dir))
            pos = step
        actions.append(('pegar', None))
        # Caminho de volta para a saída (ainda evitando o Wumpus)
        path_to_saida = bfs_evitar_wumpus(pos, saida)
        for step in path_to_saida[1:]:
            nova_dir = get_dir(pos, step)
            if direcao != nova_dir:
                actions.append(('virar', nova_dir))
                direcao = nova_dir
            actions.append(('mover', nova_dir))
            pos = step
        actions.append(('escalar', None))
        return actions
    # 2. Se não há caminho seguro, tenta matar o Wumpus
    # Caminho até ficar adjacente ao Wumpus
    def bfs_ate_adjacente_wumpus(start):
        queue = deque()
        queue.append((start, [start]))
        visited = set()
        visited.add(start)
        while queue:
            pos, path = queue.popleft()
            if adjacente_wumpus(pos):
                return path
            for d in Movimento.values():
                nx, ny = pos[0] + d[0], pos[1] + d[1]
                npos = (nx, ny)
                if 0 <= nx < tamanho and 0 <= ny < tamanho and npos not in abismos and npos not in visited and npos != wumpus:
                    visited.add(npos)
                    queue.append((npos, path + [npos]))
        return []
    path_to_adj = bfs_ate_adjacente_wumpus(pos)
    for step in path_to_adj[1:]:
        nova_dir = get_dir(pos, step)
        if direcao != nova_dir:
            actions.append(('virar', nova_dir))
            direcao = nova_dir
        actions.append(('mover', nova_dir))
        pos = step
    # Atira a flecha na direção do Wumpus
    if not flecha_usada and adjacente_wumpus(pos):
        # Descobre direção do Wumpus
        for d, delta in Movimento.items():
            nx, ny = pos[0] + delta[0], pos[1] + delta[1]
            if (nx, ny) == wumpus:
                if direcao != d:
                    actions.append(('virar', d))
                    direcao = d
                actions.append(('atirar', direcao))
                flecha_usada = True
                wumpus_morto = True
                break
    # Agora pode passar pela casa do Wumpus
    def bfs_ate_ouro_apos_matar(start):
        queue = deque()
        queue.append((start, [start]))
        visited = set()
        visited.add(start)
        while queue:
            pos, path = queue.popleft()
            if pos == ouro:
                return path
            for d in Movimento.values():
                nx, ny = pos[0] + d[0], pos[1] + d[1]
                npos = (nx, ny)
                if 0 <= nx < tamanho and 0 <= ny < tamanho and npos not in abismos and npos not in visited:
                    visited.add(npos)
                    queue.append((npos, path + [npos]))
        return []
    path_to_ouro2 = bfs_ate_ouro_apos_matar(pos)
    for step in path_to_ouro2[1:]:
        nova_dir = get_dir(pos, step)
        if direcao != nova_dir:
            actions.append(('virar', nova_dir))
            direcao = nova_dir
        actions.append(('mover', nova_dir))
        pos = step
    actions.append(('pegar', None))
    # Caminho de volta para a saída (agora pode passar pelo Wumpus)
    path_to_saida2 = bfs_ate_ouro_apos_matar(pos)
    for step in path_to_saida2[1:]:
        nova_dir = get_dir(pos, step)
        if direcao != nova_dir:
            actions.append(('virar', nova_dir))
            direcao = nova_dir
        actions.append(('mover', nova_dir))
        pos = step
    actions.append(('escalar', None))
    return actions

def agente_explorador(mundo):
    """
    Agente explora células seguras até perceber 'Brilho'. Só então planeja pegar o ouro e sair.
    """
    from collections import deque
    tamanho = mundo.tamanho
    start = mundo.jogador
    saida = (0, 0)
    abismos = set(mundo.abismos)
    wumpus = mundo.WumpusPos if mundo.Wumpusvivo else None
    visitadas = set([start])
    acoes = []
    direcao = mundo.direcao
    encontrou_brilho = False
    pos_ouro = None
    # Busca células seguras (visitadas e sem risco conhecido)
    def percepcao_brilho(pos):
        visao = mundo.visao[pos[0]][pos[1]]
        return visao and 'Brilho' in visao
    def percepcao_fedor(pos):
        visao = mundo.visao[pos[0]][pos[1]]
        return visao and 'Fedor' in visao
    # BFS para explorar células seguras
    queue = deque()
    queue.append((start, [start], direcao))
    while queue and not encontrou_brilho:
        pos, path, dir_atual = queue.popleft()
        if percepcao_brilho(pos):
            encontrou_brilho = True
            pos_ouro = pos
            caminho_ate_ouro = path
            dir_ouro = dir_atual
            break
        for d, delta in Movimento.items():
            nx, ny = pos[0] + delta[0], pos[1] + delta[1]
            npos = (nx, ny)
            if 0 <= nx < tamanho and 0 <= ny < tamanho and npos not in visitadas:
                # Não explora abismos conhecidos nem o Wumpus vivo
                conteudo = mundo.mapa[nx][ny]
                if (('A' in conteudo) or ('W' in conteudo and mundo.Wumpusvivo)):
                    continue
                visitadas.add(npos)
                queue.append((npos, path + [npos], d))
    # Se encontrou brilho, planeja pegar o ouro e sair
    if encontrou_brilho:
        # Caminho até o ouro
        pos = start
        dir_atual = direcao
        for step in caminho_ate_ouro[1:]:
            nova_dir = get_dir(pos, step)
            if dir_atual != nova_dir:
                acoes.append(('virar', nova_dir))
                dir_atual = nova_dir
            acoes.append(('mover', nova_dir))
            pos = step
        acoes.append(('pegar', None))
        # Caminho de volta para a saída
        def bfs_seguro(start, goal):
            queue = deque()
            queue.append((start, [start]))
            visited = set()
            visited.add(start)
            while queue:
                pos, path = queue.popleft()
                if pos == goal:
                    return path
                for d in Movimento.values():
                    nx, ny = pos[0] + d[0], pos[1] + d[1]
                    npos = (nx, ny)
                    if 0 <= nx < tamanho and 0 <= ny < tamanho and npos not in abismos and npos not in visited:
                        conteudo = mundo.mapa[nx][ny]
                        if ('A' in conteudo) or ('W' in conteudo and mundo.Wumpusvivo):
                            continue
                        visited.add(npos)
                        queue.append((npos, path + [npos]))
            return []
        caminho_saida = bfs_seguro(pos_ouro, saida)
        for step in caminho_saida[1:]:
            nova_dir = get_dir(pos, step)
            if dir_atual != nova_dir:
                acoes.append(('virar', nova_dir))
                dir_atual = nova_dir
            acoes.append(('mover', nova_dir))
            pos = step
        acoes.append(('escalar', None))
        return acoes
    # Se não encontrou brilho, apenas explora células seguras adjacentes
    # (pode ser expandido para explorar mais, ou tentar matar o Wumpus se sentir fedor)
    return []

def bfs_path(start, goal, abismos):
    """Retorna o caminho (lista de posições) de start até goal evitando abismos."""
    queue = deque()
    queue.append((start, [start]))
    visited = set()
    visited.add(start)
    while queue:
        pos, path = queue.popleft()
        if pos == goal:
            return path
        for d in Movimento.values():
            nx, ny = pos[0] + d[0], pos[1] + d[1]
            npos = (nx, ny)
            if 0 <= nx < 4 and 0 <= ny < 4 and npos not in abismos and npos not in visited:
                visited.add(npos)
                queue.append((npos, path + [npos]))
    return []

def get_dir(orig, dest):
    dx = dest[0] - orig[0]
    dy = dest[1] - orig[1]
    if dx == -1:
        return 'N'
    if dx == 1:
        return 'S'
    if dy == 1:
        return 'L'
    if dy == -1:
        return 'O'
    return 'L'

def menu_inicial(screen):
    selecionado = 0
    opcoes = ["Jogar como Humano", "Agente Autônomo", "Agente Explorador"]
    while True:
        screen.fill(PRETO)
        titulo = fonte_grande.render("Mundo de Wumpus", True, BRANCO)
        screen.blit(titulo, (LARGURA//2 - titulo.get_width()//2, 100))
        for i, opcao in enumerate(opcoes):
            cor = VERDE if i == selecionado else BRANCO
            texto = fonte_media.render(opcao, True, cor)
            screen.blit(texto, (LARGURA//2 - texto.get_width()//2, 220 + i*60))
        instr = fonte_pequena.render("Use ↑/↓ e Enter para escolher", True, CINZA)
        screen.blit(instr, (LARGURA//2 - instr.get_width()//2, 350))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selecionado = (selecionado - 1) % len(opcoes)
                elif event.key == pygame.K_DOWN:
                    selecionado = (selecionado + 1) % len(opcoes)
                elif event.key == pygame.K_RETURN:
                    return selecionado

def main():
    modo = menu_inicial(screen)
    mundo = Mundo()
    running = True
    agente_acoes = []
    agente_idx = 0
    agente_delay = 20  # frames entre ações
    agente_timer = 0
    if modo == 1:
        agente_acoes = bfs_wumpus(mundo)
    elif modo == 2:
        agente_acoes = agente_explorador(mundo)
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and (mundo.morto or mundo.venceu):
                    mundo = Mundo()
                    if modo == 1:
                        agente_acoes = bfs_wumpus(mundo)
                        agente_idx = 0
                        agente_timer = 0
                    elif modo == 2:
                        agente_acoes = agente_explorador(mundo)
                        agente_idx = 0
                        agente_timer = 0
                elif event.key == pygame.K_q and (mundo.morto or mundo.venceu):
                    running = False
                elif modo == 0 and not mundo.morto and not mundo.venceu:
                    if event.key == pygame.K_UP:
                        mundo.DirecaoJogador("N")
                        mundo.MoverJogador()
                    elif event.key == pygame.K_DOWN:
                        mundo.DirecaoJogador("S")
                        mundo.MoverJogador()
                    elif event.key == pygame.K_RIGHT:
                        mundo.DirecaoJogador("L")
                        mundo.MoverJogador()
                    elif event.key == pygame.K_LEFT:
                        mundo.DirecaoJogador("O")
                        mundo.MoverJogador()                        
                    elif event.key == pygame.K_f:
                        mundo.AtirarFlecha()
                    elif event.key == pygame.K_SPACE:
                        if mundo.jogador == mundo.OuroPos and mundo.ouro == True:
                            mundo.PegarOuro()
                        elif mundo.jogador == (0, 0):
                            mundo.Escalar()
                        else:
                            mundo.mensagem = "Não há ouro aqui e não é possível escalar daqui"
                    elif event.key == pygame.K_ESCAPE:
                        running = False
        # Execução do agente
        if modo in [1, 2] and not mundo.morto and not mundo.venceu:
            agente_timer += 1
            if agente_timer >= agente_delay and agente_idx < len(agente_acoes):
                acao, direcao = agente_acoes[agente_idx]
                if acao == 'virar':
                    mundo.DirecaoJogador(direcao)
                elif acao == 'mover':
                    mundo.DirecaoJogador(direcao)
                    mundo.MoverJogador()
                elif acao == 'atirar':
                    mundo.AtirarFlecha()
                    # Replaneja após atirar, pois o estado do Wumpus pode ter mudado
                    if modo == 1:
                        agente_acoes = bfs_wumpus(mundo)
                    elif modo == 2:
                        agente_acoes = agente_explorador(mundo)
                    agente_idx = -1  # será incrementado para 0 abaixo
                elif acao == 'pegar':
                    mundo.PegarOuro()
                elif acao == 'escalar':
                    mundo.Escalar()
                agente_idx += 1
                agente_timer = 0
        screen.fill(PRETO)
        mundo.desenhar(screen)
        pygame.display.flip()
        clock.tick(FPS)
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()