import g2d
import random
import datetime


class Game:
    """
    Generica classe game utilizzata durante la partita vera e propria
    """
    def __init__(self):
        self._boxes = []  # Lista delle caselle
        self._matrix = []  # Matrice con il numero di ogni casella
        self._statematrix = []  # Matrice con lo stato di ogni casella
        self._difficulty = 0
        self._startingpoint = (0, 0)
        self._origin = 0  # Punto di origine della casella in alto a sinistra
        self._boxsize = 32  # Dimensione di ogni casella
        self._totalboxes = 0  # Numero di caselle bianche totali

    def creategame(self):
        """
        Ottiene una matrice dal database, costruisce la matrice di stato corrispondente e inizializza le caselle
        """
        self._boxes = []  # Pulisce la lista delle caselle in caso non si tratti della prima partita
        self._origin = (GUI._w - self._boxsize * self._difficulty) // 2  # Centra la griglia in base al numero di righe/colonne
        self._matrix = getmatrix(self._difficulty)  # Ottiene la matrice di base dell'hitori
        self._statematrix = [[0 for _ in range(len(self._matrix))] for _ in range(len(self._matrix))]  # Riempie la matrice di stato con degli zeri
        for n in range(self._difficulty):
            for i in range(self._difficulty):
                Box(self._boxes, n, i, self._origin, self._matrix[n][i])  # Crea casella a riga n e colonna i con il numero corrispondente

    def totalboxes(self):
        self._totalboxes = 0
        for box in self._boxes:
            if ActualGame._statematrix[box._row][box._column] != 1:
                self._totalboxes += 1
        return self._totalboxes

    def check(self, finalcheck: bool):
        """
        Controlla se le condizioni di vittoria sono soddisfatte, altrimenti ritorna lo stato che verrà utilizzato per indicare cosa è sbagliato.
        """
        totalboxlist = []
        for box in self._boxes:
            if self._statematrix[box._row][box._column] == 1:  # Se la casella è nera, controlla che non ve ne siano di adiacenti
                if not blackcheck(box):
                    if finalcheck:
                        status = 1
                        return status
                    else:
                        return False
            else:
                self._startingpoint = (box._row, box._column)  # Utilizza questa casella come punto di inizio per il controllo successivo
                if not numbercheck(box):  # Altrimenti controlla se il numero è già presente nella riga/colonna
                    if finalcheck:
                        status = 2
                        return status
                    else:
                        return False
        if isolationcheck(self._startingpoint, totalboxlist, self.totalboxes()):
            """
            Controllo della lista di caselle bianche continue tra loro. La funzione, essendo ricorsiva, aggiunge più volte lo stesso valore
            alla lista, quindi vengono rimossi quelli doppi prima di effettuare il paragone.
            """
            if finalcheck:
                status = 4
                return status
            else:
                return True  # Se il programma arriva qui, le altre condizioni sono già state verificate, quindi possiamo uscire in tranquillità
        else:
            if finalcheck:
                status = 3
                return status
            else:
                return False


class Box:
    """
    Casella di gioco
    """
    def __init__(self, boxlist, row, column, origin, number):
        self._boxlist = boxlist
        self._boxlist.append(self)
        self._row = row
        self._column = column
        self._origin = origin
        self._number = number
        self._selected = False  # Casella inizialmente non selezionata
        self._x = self._origin + ActualGame._boxsize * self._column  # Posizione sul canvas in base al numero di colonna
        self._y = self._origin + ActualGame._boxsize * self._row   # Posizione sul canvas in base al numero di riga


class GUI:
    """
    Generica classe di interfaccia grafica
    """
    def __init__(self, w, h):
        self._w = w
        self._h = h
        self._state = 0  # Stato dell'interfaccia
        self._substate = 0  # Sottostato dell'interfaccia, utilizzato per messaggi temporanei in uno stato
        self._elements = []  # Lista degli elementi da disegnare
        self._gamerunning = False
        self._time = 0
        self._timer = 0
        self._subtimer = 150  # Durata di permanenza dei messaggi temporanei
        self._clicks = 0

    def changestate(self):
        """
        Disegna una UI diversa in base allo stato del gioco
        """
        self.clearui()  # Pulisce l'UI a ogni utilizzo
        if self._state == 0:  # Menu principale
            GUIElement(GUI, 200, 32, 0, 48, 0, 'Hitori', False)
            GUIElement(GUI, 200, 128, 0, 24, 0, 'Play', True)
            GUIElement(GUI, 200, 160, 0, 24, 0, 'Exit', True)
        elif self._state == 1:  # Scelta difficoltà del gioco
            GUIElement(GUI, 128, 32, 0, 24, 0, 'Choose Difficulty', False)
            for n in range(5, 13):  # Crea un pulsante per ogni numero da 5 a 12, escluso 11 che non c'è nel database
                if n < 10:
                    GUIElement(GUI, 192 + 24 * (n - 5), 128, 0, 24, 0, n, True)
                elif n == 10:
                    GUIElement(GUI, 312, 128, 0, 24, 0, n, True)
                elif n == 12:
                    GUIElement(GUI, 348, 128, 0, 24, 0, n, True)
                else:
                    pass
            GUIElement(GUI, 200, 180, 0, 24, 0, 'Back', True)
        elif self._state == 2:  # Gioco vero e proprio
            if not self._gamerunning:
                self._gamerunning = True  # Se non è già in gioco, inizia la partita
                self._clicks = 0  # Reimposta i click in caso di seconda partita
                self._time = datetime.datetime.now()  # Ottiene l'ora di inizio della partita
                ActualGame.creategame()
            GUIElement(GUI, 32, 16, 0, 24, 0, self._timer, False)   # Durata della partita. Il timer si blocca se il giocatore ha vinto
            GUIElement(GUI, 128, 16, 0, 24, 0, 'Clicks:' + str(self._clicks), False)
            if self._substate != 0:
                self._subtimer -= 1  # Se è in un sottostato, sottrai il timer
                if self._subtimer == 0:  # Una volta esaurito, se il sottostato è quello di vittoria, ritorna al menu principale
                    if self._substate == 4:
                        self._gamerunning = False
                        self._state = 0
                    self._substate = 0  # Reimposta il sottostato e il relativo timer
                    self._subtimer = 150
                if self._substate == 1:
                    GUIElement(GUI, 32, 440, 0, 18, 0, 'Some blackened boxes are adjacent to each other', False)
                elif self._substate == 2:
                    GUIElement(GUI, 16, 440, 0, 18, 0, 'Some numbers appear more than once in a row or column', False)
                elif self._substate == 3:
                    GUIElement(GUI, 96, 440, 0, 18, 0, 'Some numbers are isolated', False)
                elif self._substate == 4:
                    GUIElement(GUI, 120, 440, 0, 18, 0, 'Puzzle complete!', False)
            if self._substate != 4:
                GUIElement(GUI, 400, 16, 0, 24, 0, 'Check', True)  # Il pulsante non appare se il giocatore ha vinto
                GUIElement(GUI, 256, 16, 0, 24, 0, 'Hint', True)
                self._timer = str((datetime.datetime.now() - self._time))[2:-7]  # Differenza tra ora attuale e ora di inizio, in minuti e secondi

    def clearui(self):
        """
        Pulisce la lista degli elementi di interfaccia
        """
        for elem in self._elements[:]:
            self._elements.remove(elem)


class GUIElement:
    """
    Elemento di interfaccia, può essere testo o immagine
    """
    def __init__(self, gui, x, y, w, h, cat, text, selectable):
        self._gui = gui
        self._gui._elements.append(self)
        self._x = x
        self._y = y
        self._h = h  # Parametro utilizzato come dimensione carattere in caso di testo
        self._cat = cat  # Tipo di elemento: 0 = Testo, 1 = Immagine
        self._text = str(text)
        self._selected = False
        self._selectable = selectable  # Selezionabile o meno
        if self._cat == 0:  # Calcola dinamicamente la lunghezza della bounding box in caso di testo, con alcuni casi particolari
            if len(self._text) == 1:
                self._w = self._h / 2
            elif len(self._text) == 2:
                self._w = self._h
            else:
                self._w = (len(self._text) - 2) * self._h
        else:  # Altrimenti prende quella che viene fornita dall'utente
            self._w = w


def hint():
    changes = 0
    for box in ActualGame._boxes:
        if ActualGame._statematrix[box._row][box._column] == 0:
            if not blackcheck(box):
                ActualGame._statematrix[box._row][box._column] = 2
                changes += 1
                for subbox in ActualGame._boxes:
                    if (box._row == subbox._row or box._column == subbox._column) and box._number == subbox._number and ActualGame._statematrix[subbox._row][subbox._column] != 1 and box is not subbox:
                        ActualGame._statematrix[subbox._row][subbox._column] = 1
                        changes += 1
                        break
                break
            elif numbercheck(box):
                ActualGame._statematrix[box._row][box._column] = 1
                changes += 1
                conditionlist = [(box._row - 1, box._column), (box._row + 1, box._column), (box._row, box._column - 1), (box._row, box._column + 1)]  # Lista delle caselle da controllare
                for cond in conditionlist:
                    if cond[0] < 0 or cond[1] < 0 or cond[0] > ActualGame._difficulty - 1 or cond[1] > ActualGame._difficulty - 1:
                        continue  # Se la casella risultante ha coordinate negative o superiori alle dimensioni della griglia, ignorala
                    else:
                        ActualGame._statematrix[cond[0]][cond[1]] = 2
                        changes += 1
                        break
                break
        elif ActualGame._statematrix[box._row][box._column] == 1:
            if not blackcheck(box):
                ActualGame._statematrix[box._row][box._column] = 2
                changes += 1
                for subbox in ActualGame._boxes:
                    if (box._row == subbox._row or box._column == subbox._column) and box._number == subbox._number and ActualGame._statematrix[subbox._row][subbox._column] != 1 and box is not subbox:
                        ActualGame._statematrix[subbox._row][subbox._column] = 1
                        changes += 1
                        break
                break
            else:
                if numbercheck(box):
                    ActualGame._statematrix[box._row][box._column] = 2
                    changes += 1
                    break
        elif ActualGame._statematrix[box._row][box._column] == 2:
            if not numbercheck(box):
                ActualGame._statematrix[box._row][box._column] = 1
                changes += 1
                conditionlist = [(box._row - 1, box._column), (box._row + 1, box._column), (box._row, box._column - 1), (box._row, box._column + 1)]  # Lista delle caselle da controllare
                for cond in conditionlist:
                    if cond[0] < 0 or cond[1] < 0 or cond[0] > ActualGame._difficulty - 1 or cond[1] > ActualGame._difficulty - 1:
                        continue  # Se la casella risultante ha coordinate negative o superiori alle dimensioni della griglia, ignorala
                    else:
                        ActualGame._statematrix[cond[0]][cond[1]] = 2
                        changes += 1
                        break
                break
    if changes > 0:
        GUI._clicks += 1


def blackcheck(box: Box) -> bool:
    """
    Controlla la presenza di caselle annerite adiacenti a quella selezionata
    """
    row = box._row
    column = box._column
    conditionlist = [(row - 1, column), (row + 1, column), (row, column - 1), (row, column + 1)]  # Lista delle caselle da controllare
    for cond in conditionlist:
        if cond[0] < 0 or cond[1] < 0 or cond[0] > ActualGame._difficulty - 1 or cond[1] > ActualGame._difficulty - 1:
            continue  # Se la casella risultante ha coordinate negative o superiori alle dimensioni della griglia, ignorala
        else:
            if ActualGame._statematrix[cond[0]][cond[1]] == 1:  # Altrimenti controllane lo stato
                return False
    return True


def numbercheck(box: Box) -> bool:
    """
    Controlla la presenza di numeri identici a quello dato nella riga e colonna selezionate
    """
    for subbox in ActualGame._boxes:
        if (box._row == subbox._row or box._column == subbox._column) and box._number == subbox._number and ActualGame._statematrix[subbox._row][subbox._column] != 1 and box is not subbox:
            return False
    return True


def isolationcheck(startingpoint, totalboxlist, totalboxes):
    if len(list(set(isolationai(startingpoint, totalboxlist)))) == totalboxes:
        """
        Controllo della lista di caselle bianche continue tra loro. La funzione, essendo ricorsiva, aggiunge più volte lo stesso valore
        alla lista, quindi vengono rimossi quelli doppi prima di effettuare il paragone.
        """
        return True
    else:
        return False


def isolationai(startingpoint: (int, int), totalboxlist: list) -> list:
    """
    Controlla che nessuna casella bianca sia isolata. Ammazzatemi.
    """
    row = startingpoint[0]
    column = startingpoint[1]
    conditionlist = [(row - 1, column), (row + 1, column), (row, column - 1), (row, column + 1), (row, column)]  # Lista delle caselle da controllare
    for cond in conditionlist[:]:
        if cond[0] < 0 or cond[1] < 0 or cond[0] > ActualGame._difficulty - 1 or cond[1] > ActualGame._difficulty - 1 or cond in totalboxlist or \
                ActualGame._statematrix[cond[0]][cond[1]] == 1:
            conditionlist.remove(cond)  # Rimuovi le caselle con riga/colonna invalide, quelle già presenti nella lista finale e quelle annerite
    if len(conditionlist) != 0:  # Se c'è almeno una casella da controllare
        for cond in conditionlist:
            totalboxlist.append(cond)  # Aggiungi la casella controllata alla lista finale
            isolationai(cond, totalboxlist)  # Funzione ricorsiva
    return totalboxlist


def checkmousepos(x: int, y: int, w: int, h: int) -> bool:
    """
    Controlla se la posizione del mouse è all'interno del rettangolo di coordinate/dimensioni fornite.
    """
    x2 = g2d.mouse_position()[0]
    y2 = g2d.mouse_position()[1]
    return y < y2 < y + h and x < x2 < x + w


def checkbuttons():
    """
    Controlla se i pulsanti sono premuti e agisce di conseguenza
    """
    # --------Controllo interfaccia------- #
    for i, elem in enumerate(GUI._elements):
        if g2d.key_released('LeftButton') and elem._selectable and elem._selected:  # Prosegue solo se il pulsante è selezionabile e selezionato
            if GUI._state == 0:  # Menu principale
                if i == 1:  # Pulsante Play
                    GUI._state = 1
                elif i == 2:  # Pulsante Quit
                    g2d.close_canvas()
                break  # Non serve controllare tutto
            elif GUI._state == 1:  # Menu selezione difficoltà
                if 1 <= i < len(GUI._elements) - 1:
                    ActualGame._difficulty = int(elem._text)  # Imposta la difficoltà in base al numero selezionato e inizia la partita
                    GUI._state = 2
                else:  # Pulsante Back
                    GUI._state = 0
                break  # Non serve controllare tutto
            elif GUI._state == 2:  # Partita vera e propria
                if i == len(GUI._elements) - 2:  # Pulsante Check
                    GUI._substate = ActualGame.check(True)
                elif i == len(GUI._elements) - 1:
                    hint()
    # --------Controllo caselle------- #
    if GUI._gamerunning:  # Effettua il controllo solo se in partita
        for box in ActualGame._boxes:
            if g2d.key_released('LeftButton') and box._selected:
                GUI._clicks += 1  # Aumenta il numero di click
                if ActualGame._statematrix[box._row][box._column] == 2:  # Se cerchiato, ritorna allo stato normale
                    ActualGame._statematrix[box._row][box._column] = 0
                else:
                    ActualGame._statematrix[box._row][box._column] += 1  # Altrimenti passa a quello successivo


def getmatrix(difficulty: int) -> list:
    """
    Fa il lavoro sporco di ottenere la matrice dal database e sistemarla per la classe Game
    """
    matrix = [[] for _ in range(difficulty)]  # Aggiunge una lista vuota per ogni riga
    with open('db.txt') as file:
        db = file.read().split('\n')  # Separa ogni riga
        while True:
            num = random.randint(0, 699)  # Sceglie uno schema a caso
            line = list(db[num].split(','))  # Trasforma la riga corrispondente in lista e rimuove le virgole
            if len(line) == difficulty ** 2:  # Se lo schema è della lunghezza giusta lo tiene, altrimenti ne sceglie un altro
                break
        for nam, num in enumerate(line):
            matrix[nam // difficulty].append(int(num))  # Aggiunge il numero alla riga giusta della matrice in base alla sua posizione nella lista
        return matrix


def drawline(origin: int, size: int, gridsize: int, pos: int):
    """
    Disegna una linea in base all origine, dimensione delle caselle e la riga/colonna date
    """
    g2d.draw_line((origin + size * pos, origin), (origin + size * pos, origin + size * gridsize))  # Linea verticale
    g2d.draw_line((origin, origin + size * pos), (origin + size * gridsize, origin + size * pos))  # Linea orizzontale


def update():
    """
    Funzione principale di update
    """
    GUI.changestate()  # Aggiorna l'interfaccia
    g2d.clear_canvas()
    g2d.set_color((0, 0, 0))
    if GUI._gamerunning:  # Solo se in partita
        # --------Disegno linee------- #
        for n in range(0, ActualGame._difficulty + 1):
            drawline(ActualGame._origin, ActualGame._boxsize, ActualGame._difficulty, n)
        # --------Disegno caselle------- #
        for box in ActualGame._boxes:
            if ActualGame._statematrix[box._row][box._column] == 2:  # Stato cerchiato
                g2d.fill_circle((box._x + ActualGame._boxsize / 2, box._y + ActualGame._boxsize / 2), ActualGame._boxsize / 2)  # Disegna un cerchio nero che riempie la casella
                g2d.set_color((255, 255, 255))
                g2d.fill_circle((box._x + ActualGame._boxsize / 2, box._y + ActualGame._boxsize / 2), ActualGame._boxsize / 2 - 2)  # Disegna un cerchio bianco più piccolo per dare l'illusione di contorno
                g2d.set_color((0, 0, 0))  # Reimposta a nero per disegnare il resto
            if ActualGame._statematrix[box._row][box._column] != 1:
                if len(str(box._number)) == 1:
                    g2d.draw_text(str(box._number), (box._x + ActualGame._boxsize // 5, box._y + ActualGame._boxsize // 6), ActualGame._boxsize / 4 * 3)  # Disegna il testo in modo più o meno centrato
                else:
                    g2d.draw_text(str(box._number), (box._x + ActualGame._boxsize // 16, box._y + ActualGame._boxsize // 6), ActualGame._boxsize / 4 * 3)  # Disegna il testo in modo più o meno centrato
            else:
                g2d.fill_rect((box._x, box._y, ActualGame._boxsize, ActualGame._boxsize))  # Se lo stato è 1, disegna invece un rettangolo
            # --------Controllo selezione caselle------- #
            box._selected = False  # Resetta lo stato di selezione
            if checkmousepos(box._x, box._y, ActualGame._boxsize, ActualGame._boxsize):  # Se il mouse si trova all'interno di una casella, marcala come selezionata
                box._selected = True
    # --------Disegno interfaccia------- #
    for elem in GUI._elements:
        if checkmousepos(elem._x, elem._y, elem._w, elem._h) and elem._selectable:  # Se il mouse si trova nella bounding box del pulsante, marcalo come selezionato
            elem._selected = True
        if elem._selected:
            g2d.set_color((255, 0, 0))  # I pulsanti selezionati sono disegnati in rosso
        else:
            g2d.set_color((0, 0, 0))  # Gli altri in nero
        if elem._cat == 0:
            g2d.draw_text(elem._text, (elem._x, elem._y), elem._h)  # Se è del testo
        else:
            g2d.draw_image((elem._x, elem._y), (elem._w, elem._h))  # Se è un'immagine
    # --------Controllo pulsanti------- #
    checkbuttons()


def main():
    """
    Ed è qui che tutto ebbe inizio...
    """
    g2d.init_canvas((GUI._w, GUI._h))
    g2d.main_loop(update)


ActualGame = Game()
GUI = GUI(500, 500)
main()
