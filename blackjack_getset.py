import pygame
from pygame.locals import *
import random
import os

#classe que cria as cartas
class Card:
    def __init__(self, suit, value, image_path):
        self._suit = suit
        self._value = value
        self._image = pygame.image.load(image_path)

    @property
    def suit(self):
        return self._suit

    @suit.setter
    def suit(self, suit):
        self._suit = suit

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value

    @property
    def image(self):
        return self._image

    @image.setter
    def image(self, image):
        self._image = image

    @property
    def amount(self):
        # define o valor das cartas
        if self._value in ['J', 'Q', 'K']:
            return 10
        elif self._value == 'A':
            return 11
        else:
            return int(self._value)

# classe que cria o baralho de cartas
class Deck:
    def __init__(self, resource_path):
        self._cards = []
        suits = ['d', 'c', 'h', 's']
        values = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        for suit in suits:
            for value in values:
                image_path = os.path.join(resource_path, f'cards/{suit}{value}.png')
                self._cards.append(Card(suit, value, image_path))
        random.shuffle(self._cards)

    @property
    def cards(self):
        return self._cards

    @cards.setter
    def cards(self, cards):
        self._cards = cards

    #função de compra de cartas, que compra do final da lista
    def draw_card(self):
        return self._cards.pop()

# classe do jogador
class User:
    def __init__(self):
        self._cards = []
        self._sum = 0
        self._aces = 0

    @property
    def cards(self):
        return self._cards

    @cards.setter
    def cards(self, cards):
        self._cards = cards

    @property
    def sum(self):
        return self._sum

    @sum.setter
    def sum(self, sum):
        self._sum = sum

    @property
    def aces(self):
        return self._aces

    @aces.setter
    def aces(self, aces):
        self._aces = aces


    #função de comprar cartas
    def add_card(self, card):
        self._cards.append(card)
        self._sum += card.amount
        if card.value == 'A':
            self._aces += 1
        self.adjust_for_ace()

    # ajusta o valor do ás caso a mão ultrapasse 21
    def adjust_for_ace(self):
        while self._sum > 21 and self._aces:
            self._sum -= 10
            self._aces -= 1

# classe do dealer, que herda os atributos de Player
class Dealer(User):
    def __init__(self):
        super().__init__()

    # função com a lógica de jogo do dealer
    def play(self, deck, user_sum):
        while self.sum <= user_sum and self.sum < 17:
            self.add_card(deck.draw_card())
        return self.sum


# classe da engine do jogo
class Game:
    def __init__(self, screen):
        self.screen = screen
        self.background_color = (73, 148, 10)
        self._gray = (192, 192, 192)
        self._black = (0, 0, 0)
        self._white = (255, 255, 255)
        self._font = pygame.font.SysFont('arial', 15)
        self._hit_button = pygame.Rect(10, 445, 75, 25)
        self._stand_button = pygame.Rect(95, 445, 75, 25)
        self._restart_button = pygame.Rect(245, 235, 125, 25)
        self.win_count = 0
        self.loss_count = 0

        self._deck = Deck('resources')
        self._card_back = pygame.image.load('resources/cards/cardback.png')
        self._icon = pygame.image.load('resources/icon.png')
        pygame.display.set_icon(self._icon)

        self.user = User()
        self.dealer = Dealer()
        self._stand = False
        self._game_over = False
        self._result_text = ""

        self.initialize_game()

    #função de inicializar o jogo e distribuir duas cartas para o jogador e pro dealer
    def initialize_game(self):
        pygame.init()
        self.screen.fill(self.background_color)
        self._hit_text = self._font.render('Hit', 1, self._black)
        self._stand_text = self._font.render('Stand', 1, self._black)
        self._restart_text = self._font.render('Jogar novamente', 1, self._black)

        for _ in range(2):
            self.user.add_card(self._deck.draw_card())
            self.dealer.add_card(self._deck.draw_card())


    #função gráfica do Pygame, com background, posição das cartas, configurações dos botões e textos
    def update_screen(self):
        self.screen.fill(self.background_color)

        pygame.draw.rect(self.screen, self._gray, self._hit_button)
        self.screen.blit(self._hit_text, (39, 448))

        pygame.draw.rect(self.screen, self._gray, self._stand_button)
        self.screen.blit(self._stand_text, (116, 448))

        win_text = self._font.render(f'Vitorias: {self.win_count}', 1, self._black)
        lose_text = self._font.render(f'Derrotas: {self.loss_count}', 1, self._black)
        self.screen.blit(win_text, (562, 413))
        self.screen.blit(lose_text, (555, 438))

        for i, card in enumerate(self.dealer.cards):
            x = 10 + i * 110
            self.screen.blit(card.image, (x, 10))
        if not self._game_over and not self._stand:
            self.screen.blit(self._card_back, (120, 10))

        for i, card in enumerate(self.user.cards):
            x = 10 + i * 110
            self.screen.blit(card.image, (x, 295))

        if self._game_over or self._stand:
            result_display_text = self._font.render(self._result_text, 1, self._black)
            text_rect = result_display_text.get_rect(center=(308, 210))
            pygame.draw.rect(self.screen, self._gray, text_rect.inflate(20, 10))
            self.screen.blit(result_display_text, text_rect.topleft)

            pygame.draw.rect(self.screen, self._gray, self._restart_button)
            self.screen.blit(self._restart_text, (251, 240))
            self.screen.blit(self.dealer.cards[1].image, (120, 10))
        pygame.display.update()

    #função do pygame de fechar o jogo, e dos botões, de hit, stand e jogar novamente
    def handle_event(self, event):
        if event.type == QUIT:
            pygame.quit()
            exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if not (self._game_over or self._stand) and self._hit_button.collidepoint(pygame.mouse.get_pos()):
                self.hit()
            elif not self._game_over and self._stand_button.collidepoint(pygame.mouse.get_pos()):
                self.stand_action()
            elif (self._game_over or self._stand) and self._restart_button.collidepoint(pygame.mouse.get_pos()):
                self.restart()

    #Ao clicar em hit, adiciona uma carta à mão do player, e caso passe de 21, perde automaticamente.
    def hit(self):
        self.user.add_card(self._deck.draw_card())
        if self.user.sum > 21:
            self._result_text = "Voce perdeu!"
            self.loss_count += 1
            self._game_over = True

    #Ao dar stand, para de comprar e passa a vez para o dealer.
    def stand_action(self):
        self._stand = True
        self.dealer.play(self._deck, self.user.sum)
        self.check_winner()

    #Verifica o vencedor, ou empate.
    def check_winner(self):
        if self.user.sum > 21:
            self._result_text = "Voce perdeu!"
            self.loss_count += 1
        elif self.dealer.sum > 21:
            self._result_text = "Voce ganhou!"
            self.win_count += 1
        elif self.user.sum > self.dealer.sum:
            self._result_text = "Voce ganhou!"
            self.win_count += 1
        elif self.dealer.sum > self.user.sum:
            self._result_text = "Voce perdeu!"
            self.loss_count += 1
        else:
            self._result_text = "Empate!"
        self._game_over = True

    #reinicia o jogo ao clicar em jogar novamente
    def restart(self):
        self.user = User()
        self.dealer = Dealer()
        self._deck = Deck('resources')
        self._stand = False
        self._game_over = False
        self._result_text = ""
        self.initialize_game()

def main():
    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    pygame.display.set_caption('Blackjack')
    game = Game(screen)

    while True:
        for event in pygame.event.get():
            game.handle_event(event)
        game.update_screen()

if __name__ == '__main__':
    main()
