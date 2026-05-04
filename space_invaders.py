import turtle, math, random, time

# INÍCIO DO JOGO, INTERFACE E RANKING

# Configurações de Tela e Formatos
screen = turtle.Screen()
screen.bgcolor("black")
screen.title("Space Invaders")
screen.tracer(0) 
screen.setup(width=600, height=600)

nave_shape = ((-10,-10), (0,15), (10,-10), (0,-5))
screen.register_shape("nave", nave_shape)
inimigo_shape = ((-10,10), (10,10), (15,-5), (10,-15), (-10,-15), (-15,-5))
screen.register_shape("alien", inimigo_shape)

# Visual e Ranking
def desenhar_estrelas():
    estrela = turtle.Turtle()
    estrela.hideturtle(); estrela.speed(0); estrela.penup()
    for _ in range(80):
        estrela.setposition(random.randint(-290, 290), random.randint(-290, 290))
        estrela.dot(random.randint(1, 4), random.choice(["white", "light blue", "yellow", "gray"]))

def limpar_tela():
    for t in screen.turtles(): t.hideturtle(); t.clear()
    def vazio(): pass
    for key in ["Left", "Right", "Up", "Down", "space"]: screen.onkeypress(vazio, key)
    screen.onclick(lambda x,y: None)

def carregar_ranking():
    ranking = []
    try:
        with open("ranking.txt", "r") as f:
            for line in f:
                d = line.strip().split(",")
                if len(d) == 2: ranking.append((d[0], int(d[1])))
    except: pass
    return sorted(ranking, key=lambda x: x[1], reverse=True)

def salvar_pontuacao(nome, pontos):
    try:
        with open("ranking.txt", "a") as f: f.write(f"{nome},{pontos}\n")
    except: pass

def tela_game_over(nome, pontuacao):
    salvar_pontuacao(nome, pontuacao)
    limpar_tela()
    pen = turtle.Turtle()
    pen.speed(0); pen.penup(); pen.hideturtle()
    
    pen.setposition(0, 150); pen.color("#ff3333")
    pen.write("FIM DE JOGO", align="center", font=("Courier", 36, "bold"))
    
    pen.color("gold"); pen.setposition(0, 90)
    pen.write("RANKING DOS JOGADORES", align="center", font=("Courier", 18, "bold"))
    ranking = carregar_ranking()
    for i in range(min(5, len(ranking))):
        pen.setposition(0, 50 - (i * 30)); pen.color("white")
        pen.write(f"{i+1}. {ranking[i][0]} - {ranking[i][1]}", align="center", font=("Courier", 14, "normal"))
    
    btn = turtle.Turtle()
    btn.speed(0); btn.hideturtle(); btn.penup(); btn.setposition(-80, -120)
    btn.pendown(); btn.color("#00cc66"); btn.begin_fill()
    for _ in range(2): btn.forward(160); btn.left(90); btn.forward(40); btn.left(90)
    btn.end_fill(); btn.penup(); btn.color("white"); btn.setposition(0, -112)
    btn.write("RECOMEÇAR", align="center", font=("Courier", 14, "bold"))
    
    screen.onclick(lambda x, y: iniciar_jogo() if -80 <= x <= 80 and -120 <= y <= -80 else None)
    screen.update()

def iniciar_jogo():
    limpar_tela()
    desenhar_estrelas()
    nome_jogador = screen.textinput("Space Invaders", "Digite seu nome:") or "Anonimo"

    # Jogador e Placar
    jogador = turtle.Turtle()
    jogador.color("cyan"); jogador.shape("nave"); jogador.shapesize(1.5, 1.5)
    jogador.penup(); jogador.speed(0); jogador.setposition(0, -250); jogador.setheading(90)
    
    vel_jog = 15; pontuacao = 0; nivel = 1
    ui_pen = turtle.Turtle()
    ui_pen.speed(0); ui_pen.color("gold"); ui_pen.penup(); ui_pen.hideturtle()
    ui_pen.setposition(-280, 260)
    
    def atualizar_ui():
        ui_pen.clear()
        ui_pen.write(f"{nome_jogador} - Nível: {nivel} - Pontos: {pontuacao}", align="left", font=("Courier", 14, "bold"))
    atualizar_ui()

    # MOVIMENTAÇÃO, COLISÃO E BÔNUS 

    inimigos = []
    linhas, colunas = 3, 6
    cores = ["red", "magenta", "orange", "#ff6666"]
    for l in range(linhas):
        linha = []
        for c in range(colunas):
            i = turtle.Turtle()
            i.hideturtle(); i.penup(); i.speed(0); i.shape("alien"); i.shapesize(1.2, 1.2)
            linha.append(i)
        inimigos.append(linha)

    vel_ini_base = 0.5; vel_ini = vel_ini_base; vel_ini_y = 40

    def configurar_nivel():
        nonlocal vel_ini
        vel_ini = min(4, vel_ini_base + (nivel - 1) * 0.3)
        for l in range(linhas):
            for c in range(colunas):
                inimigos[l][c].setposition(-200 + (c * 70), 200 - (l * 50))
                inimigos[l][c].color(random.choice(cores)); inimigos[l][c].showturtle()
        
        msg = turtle.Turtle()
        msg.speed(0); msg.color("white"); msg.penup(); msg.hideturtle()
        msg.write(f"NÍVEL {nivel}", align="center", font=("Courier", 30, "bold"))
        screen.update(); time.sleep(1); msg.clear()

    configurar_nivel()

    # Disparos e bônus
    tiros = []
    for _ in range(20):
        t = turtle.Turtle()
        t.color("yellow"); t.shape("triangle"); t.penup(); t.speed(0)
        t.setheading(90); t.shapesize(0.5, 0.5); t.hideturtle()
        tiros.append(t)
    vel_tiro = 5; tipo_tiro = "normal"

    bonus = turtle.Turtle()
    bonus.shape("circle"); bonus.shapesize(0.8, 0.8); bonus.penup(); bonus.hideturtle()
    tipo_bonus = "nenhum"

    def colide(t1, t2):
        return math.sqrt((t1.xcor()-t2.xcor())**2 + (t1.ycor()-t2.ycor())**2) < 20

    # Lógica do bônus
    def processar_bonus():
        nonlocal tipo_tiro
        if bonus.isvisible():
            bonus.sety(bonus.ycor() - 2)
            if colide(jogador, bonus): bonus.hideturtle(); tipo_tiro = tipo_bonus
            elif bonus.ycor() < -300: bonus.hideturtle()

    def mover_inimigos():
        nonlocal vel_ini, jogando, game_over
        mudar_dir = False
        for linha in inimigos:
            for i in linha:
                if i.isvisible():
                    i.setx(i.xcor() + vel_ini)
                    if i.xcor() > 280 or i.xcor() < -280: mudar_dir = True
                    if colide(jogador, i) or i.ycor() < -250: jogando = False; game_over = True; return
        if mudar_dir:
            vel_ini *= -1 
            for linha in inimigos:
                for i in linha: i.sety(i.ycor() - vel_ini_y)

    def checar_colisoes():
        nonlocal pontuacao, vel_ini, tipo_bonus
        for linha in inimigos:
            for i in linha:
                if i.isvisible():
                    for t in tiros:
                        if t.isvisible() and colide(t, i):
                            t.hideturtle(); t.setposition(0, -400); i.hideturtle(); pontuacao += 10
                            if random.random() < 0.15 and not bonus.isvisible():
                                bonus.setposition(i.xcor(), i.ycor()); tipo_bonus = random.choice(["duplo", "triplo", "rapido"])
                                bonus.color({"duplo":"blue", "triplo":"green", "rapido":"purple"}[tipo_bonus]); bonus.showturtle()
                            vel_ini += 0.05 if vel_ini > 0 else -0.05
                            atualizar_ui()

    def mover_tiros():
        for t in tiros:
            if t.isvisible():
                t.sety(t.ycor() + (vel_tiro * 2 if tipo_tiro == "rapido" else vel_tiro))
                if t.ycor() > 275: t.hideturtle()

    # Movimentação e categoria do disparo
    def esq(): jogador.setx(max(-280, jogador.xcor() - vel_jog))
    def dir(): jogador.setx(min(280, jogador.xcor() + vel_jog))
    def up(): jogador.sety(min(280, jogador.ycor() + vel_jog))
    def down(): jogador.sety(max(-280, jogador.ycor() - vel_jog))

    def atirar():
        nonlocal tipo_tiro
        esc = [t for t in tiros if not t.isvisible()]
        vis = len(tiros) - len(esc)
        if tipo_tiro == "normal" and vis < 3 and len(esc) >= 1:
            esc[0].setposition(jogador.xcor(), jogador.ycor() + 10); esc[0].showturtle()
        elif tipo_tiro == "duplo" and vis < 6 and len(esc) >= 2:
            esc[0].setposition(jogador.xcor()-15, jogador.ycor()+10); esc[0].showturtle()
            esc[1].setposition(jogador.xcor()+15, jogador.ycor()+10); esc[1].showturtle()
        elif tipo_tiro == "triplo" and vis < 9 and len(esc) >= 3:
            for j, d in enumerate([-20, 0, 20]):
                esc[j].setposition(jogador.xcor()+d, jogador.ycor()+(15 if d==0 else 5)); esc[j].showturtle()
        elif tipo_tiro == "rapido" and vis < 8 and len(esc) >= 1:
            esc[0].setposition(jogador.xcor(), jogador.ycor() + 10); esc[0].showturtle()

    screen.listen()
    screen.onkeypress(esq, "Left"); screen.onkeypress(dir, "Right")
    screen.onkeypress(up, "Up"); screen.onkeypress(down, "Down")
    screen.onkeypress(atirar, "space")

    # ==========================================================
    # LOOP DO JOGO E FIM DE JOGO
    # ==========================================================

    jogando = True; game_over = False
    while jogando:
        try: screen.update() 
        except: break
            
        processar_bonus()
        mover_inimigos()
        checar_colisoes()
        mover_tiros()

        # Checar se o nível acabou
        if not any(i.isvisible() for linha in inimigos for i in linha):
            nivel += 1
            for t in tiros: t.hideturtle(); t.setposition(0, -400)
            jogador.setposition(0, -250); atualizar_ui(); configurar_nivel()

    if game_over: tela_game_over(nome_jogador, pontuacao)

# Início do jogo
try:
    iniciar_jogo()
    turtle.done()
except: pass
