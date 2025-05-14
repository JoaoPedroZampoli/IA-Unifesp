import random
import numpy as np
import pygame
import sys

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

def main():
    mundo = Mundo()
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # Processar eventos apenas se o jogo não terminou
            if not mundo.morto and not mundo.venceu:
                if event.type == pygame.KEYDOWN:
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
            else:
                # Opções para quando o jogo terminar
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        mundo = Mundo()  # Reiniciar o jogo
                    elif event.key == pygame.K_q:
                        running = False
        
        # Limpar a tela
        screen.fill(PRETO)
        
        # Desenhar o mundo
        mundo.desenhar(screen)
        
        # Atualizar a tela
        pygame.display.flip()
        
        # Controle de FPS
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()