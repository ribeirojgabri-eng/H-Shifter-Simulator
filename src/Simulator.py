import pygame
import sys
import math
import time

# --- INICIALIZAÇÃO DO SISTEMA ---
pygame.init()
WIDTH, HEIGHT = 1024, 768
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Concept S - Full Powertrain & H-Shifter Simulator")

# Cores (Paleta Otimizada)
COLOR_BG = (15, 15, 15)
COLOR_PANEL = (30, 30, 30)
COLOR_TEXT = (240, 240, 240)
COLOR_TEXT_MUTED = (150, 150, 150)
COLOR_GEAR_ACTIVE = (0, 255, 100)
COLOR_SHIFTER_LINE = (80, 80, 80)
COLOR_NEEDLE = (255, 50, 50)
COLOR_ALERT = (255, 180, 0)

# Fontes
font_large = pygame.font.SysFont("Consolas", 36, bold=True)
font_medium = pygame.font.SysFont("Arial", 22, bold=True)
font_small = pygame.font.SysFont("Arial", 16)

# --- 1. PARÂMETROS DE FÍSICA E DINÂMICA ---
MASSA_CARRO = 1240.0         # kg
RAIO_PNEU = 0.32              # metros (rd)
FINAL_DRIVE = 3.27            # Relação do Diferencial
RPM_MAX = 6500.0
RPM_IDLE = 900.0
RPM_STALL = 650.0
ACCEL_RPM_SEC = 4500.0       
DECEL_RPM_SEC = 2500.0       

# ARQUITETURA CORRIGIDA: Relação de ré é nativamente negativa para fins vetoriais
RELACOES_MARCHA = {
    'N': 0.0,
    '1': 3.83, '2': 2.36, '3': 1.55, 
    '4': 1.16, '5': 0.92, '6': 0.75, 'R': -3.50
}

C_AERODINAMICO = 0.35 * 2.1 * 1.225 / 2.0
C_ROLAMENTO = 0.015 * MASSA_CARRO * 9.81

# Estados iniciais do Powertrain
car_velocity = 0.0            # m/s (Positivo = Frente, Negativo = Ré)
engine_rpm = RPM_IDLE         
marcha_atual = 'N'
motor_ligado = True
clutch_engagement = 1.0       # 1.0 = Acoplado, 0.0 = Desacoplado
CLUTCH_ENGAGE_SPEED = 5.0     
CLUTCH_DISENGAGE_SPEED = 15.0 

# --- 2. CONFIGURAÇÃO DO LAYOUT DO H-SHIFTER ---
cx, cy = 780, 450             
dist_x, dist_y = 60, 70
layout_marchas = {
    '1': (cx - dist_x, cy - dist_y),
    '3': (cx, cy - dist_y),
    '5': (cx + dist_x, cy - dist_y),
    'R': (cx - (dist_x * 2), cy + dist_y),
    '2': (cx - dist_x, cy + dist_y),
    '4': (cx, cy + dist_y),
    '6': (cx + dist_x, cy + dist_y)
}
shifter_pos_travada = (cx, cy)
RAIO_ENGATE = 35 

# --- 3. FUNÇÕES UTILITÁRIAS DE FÍSICA ---
def encontrar_marcha_mais_proxima(mouse_pos):
    menor_distancia = float('inf')
    marcha_perto = 'N'
    for nome, pos in layout_marchas.items():
        dist = math.hypot(mouse_pos[0] - pos[0], mouse_pos[1] - pos[1])
        if dist < menor_distancia:
            menor_distancia = dist
            marcha_perto = nome                
    if menor_distancia > RAIO_ENGATE:         
        return 'N', (cx, cy)
    return marcha_perto, layout_marchas[marcha_perto]

def obter_torque_motor(rpm):
    if rpm < 400 or rpm > RPM_MAX: 
        return 0.0 
    return 280.0 - ((rpm - 4200.0) ** 2) * 0.000012

clock = pygame.time.Clock()
last_time = time.perf_counter()


# --- LOOP PRINCIPAL ---
while True:
    now = time.perf_counter()
    dt = min(now - last_time, 0.1)
    last_time = now

    keys = pygame.key.get_pressed()
    ctrl_pressionado = keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]
    acelerador_pressionado = keys[pygame.K_SPACE] if motor_ligado else False
    mouse_pos = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_e:
                if ctrl_pressionado or marcha_atual == 'N':
                    motor_ligado = True
                    engine_rpm = RPM_IDLE
                    print(">> MOTOR LIGADO <<")

    # --- GERENCIAMENTO DA EMBREAGEM E TRANSMISSÃO ---
    if ctrl_pressionado:
        clutch_engagement = max(0.0, clutch_engagement - CLUTCH_DISENGAGE_SPEED * dt)
        proxima_marcha, coords = encontrar_marcha_mais_proxima(mouse_pos)
        if proxima_marcha != marcha_atual:
            marcha_atual = proxima_marcha
            shifter_pos_travada = coords
    else:
        clutch_engagement = min(1.0, clutch_engagement + CLUTCH_ENGAGE_SPEED * dt)

    # --- 4. DINÂMICA VEICULAR VEICULADA (VETORIAL CORRIGIDA) ---
    # As forças de resistência sempre atuam contra a direção do movimento real do carro
    sentido_velocidade = 1.0 if car_velocity >= 0 else -1.0
    f_aerodinamica = C_AERODINAMICO * (car_velocity ** 2) * sentido_velocidade
    f_rolamento = (C_ROLAMENTO * sentido_velocidade) if abs(car_velocity) > 0.01 else 0.0
    f_resistencia_total = f_aerodinamica + f_rolamento
    
    relacao_atual = RELACOES_MARCHA[marcha_atual]
    forca_trativa = 0.0

    if motor_ligado:
        base_torque = obter_torque_motor(engine_rpm)
        
        if marcha_atual == 'N' or clutch_engagement < 0.3:
            torque_extra_idle = max(0.0, (RPM_IDLE - engine_rpm) * 12.0)
        else:
            torque_extra_idle = max(0.0, (RPM_IDLE - engine_rpm) * 4.0)
        
        if acelerador_pressionado:
            torque_motor_total = base_torque + torque_extra_idle
        else:
            freio_motor_dinamico = -50.0 - (engine_rpm * 0.02)
            torque_motor_total = freio_motor_dinamico + (torque_extra_idle * 0.1)
            
        torque_transmissao = torque_motor_total * clutch_engagement
        
        # O sinal de negativo da marcha ré agora é herdado diretamente de 'relacao_atual' (-3.50)
        torque_roda = torque_transmissao * relacao_atual * FINAL_DRIVE * 0.88
                
        if marcha_atual != 'N':
            forca_trativa = torque_roda / RAIO_PNEU
    else:
        # Efeito de freio motor com ignição desligada (Respeitando direção vetorial)
        if marcha_atual != 'N' and clutch_engagement > 0.0:
            arrasto_motor_morto = -180.0 * abs(relacao_atual) * clutch_engagement * sentido_velocidade
            forca_trativa = (arrasto_motor_morto * FINAL_DRIVE) / RAIO_PNEU
    
    # Força líquida balanceada vetorialmente: Força Trativa empurra, Resistência se opõe
    forca_liquida = forca_trativa - f_resistencia_total
    aceleracao = forca_liquida / MASSA_CARRO
    car_velocity += aceleracao * dt
        
    # Zona morta absoluta para imobilização do veículo
    if abs(car_velocity) < 0.05 and not acelerador_pressionado:
        if marcha_atual == 'N' or not motor_ligado or clutch_engagement < 0.1:
            car_velocity = 0.0

    # --- 5. SINCRONIZAÇÃO DE CINEMÁTICA ROTACIONAL (RPM CORRIGIDO COM ANTI-STALL VETORIAL) ---
    if motor_ligado:
        if marcha_atual != 'N' and clutch_engagement > 0.0:
            # Rotação nominal vinda das rodas
            rpm_transmissao = (abs(car_velocity) * 60.0 * abs(relacao_atual) * FINAL_DRIVE) / (2.0 * math.pi * RAIO_PNEU)
            
            if acelerador_pressionado:
                # Se houver carga no acelerador, o motor tenta subir o giro
                rpm_alvo = max(rpm_transmissao, RPM_STALL - 50.0)
                engine_rpm += (rpm_alvo - engine_rpm) * clutch_engagement * 15.0 * dt
            else:
                # Sem acelerador, o motor é severamente arrastado pela carga mecânica do carro parado
                rpm_alvo = rpm_transmissao
                # Se o carro está quase parado e soltando embreagem, força o RPM para baixo rápido (peso do carro)
                if abs(car_velocity) < 0.2 and clutch_engagement > 0.3:
                    engine_rpm += (rpm_alvo - engine_rpm) * clutch_engagement * 25.0 * dt
                else:
                    engine_rpm += (rpm_alvo - engine_rpm) * clutch_engagement * 15.0 * dt
            
            # Patinação da embreagem sob aceleração
            if acelerador_pressionado and clutch_engagement < 0.9:
                engine_rpm += ACCEL_RPM_SEC * dt * (1.0 - clutch_engagement)

            # CRÍTICO: Validação do ponto de Stall Mecânico (Funciona para frente e para trás)
            # Se o RPM cair abaixo do aceitável com a embreagem presa, e o carro não estiver correndo para segurar o giro...
            if engine_rpm < RPM_STALL and clutch_engagement > 0.5:
                # Se a velocidade do carro não for compatível com o RPM mínimo de sobrevivência, o motor morre
                rpm_minimo_sobrevivencia = (RPM_STALL * 2.0 * math.pi * RAIO_PNEU) / (60.0 * abs(relacao_atual) * FINAL_DRIVE)
                if abs(car_velocity) < rpm_minimo_sobrevivencia * 0.8:
                    print(">> MOTOR MORREU (STALL EM MARCHA RÉ/FRENTE) <<")
                    motor_ligado = False
                    engine_rpm = 0.0
        else:
            # Comportamento em Neutro / Embreagem totalmente pressionada
            if acelerador_pressionado:
                engine_rpm += ACCEL_RPM_SEC * dt
            else:
                engine_rpm -= DECEL_RPM_SEC * dt
            
            # Retorno suave para a marcha lenta
            if engine_rpm < RPM_IDLE:
                engine_rpm += (RPM_IDLE - engine_rpm) * 8.0 * dt

        # Limitador de Giro (Rev Limiter) mecânico simples
        if engine_rpm >= RPM_MAX:
            engine_rpm = RPM_MAX - 180.0
            
    # --- 6. RENDERIZAÇÃO GRÁFICA OTIMIZADA ---
    screen.fill(COLOR_BG)
    velocidade_kmh = car_velocity * 3.6
        
    pygame.draw.rect(screen, COLOR_PANEL, (50, 50, 450, 300), border_radius=10)
    
    # Exibe a velocidade em módulo para o velocímetro não marcar negativo de ré (padrão automotivo)
    txt_vel = font_large.render(f"{int(round(abs(velocidade_kmh)))} km/h", True, COLOR_TEXT)
    screen.blit(txt_vel, (80, 80))
        
    rpm_display_color = COLOR_ALERT if engine_rpm > 6000 else (COLOR_NEEDLE if not motor_ligado else COLOR_TEXT)
    rpm_text = f"RPM: {int(engine_rpm)}" if motor_ligado else "MOTOR DESLIGADO"
    txt_rpm = font_medium.render(rpm_text, True, rpm_display_color)
    screen.blit(txt_rpm, (80, 140))
        
    txt_marcha = font_large.render(f"MARCHA: {marcha_atual}", True, COLOR_GEAR_ACTIVE if marcha_atual != 'N' else COLOR_ALERT)
    screen.blit(txt_marcha, (80, 200))
        
    pygame.draw.rect(screen, (50, 50, 50), (80, 270, 200, 20))
    pygame.draw.rect(screen, COLOR_GEAR_ACTIVE, (80, 270, int(200 * clutch_engagement), 20))
    txt_fric = font_small.render(f"Fricção: {int(clutch_engagement * 100)}%", True, COLOR_TEXT)
    screen.blit(txt_fric, (290, 270))
    
    t_cx, t_cy = 270, 530
    pygame.draw.circle(screen, COLOR_PANEL, (t_cx, t_cy), 140)
    angulo_rpm = -225 + (engine_rpm / RPM_MAX) * 270
    rad_rpm = math.radians(angulo_rpm)
    end_x = int(t_cx + 120 * math.cos(rad_rpm))
    end_y = int(t_cy + 120 * math.sin(rad_rpm))
    pygame.draw.line(screen, COLOR_NEEDLE, (t_cx, t_cy), (end_x, end_y), 4)
    
    pygame.draw.rect(screen, COLOR_PANEL, (580, 50, 400, 670), border_radius=10)
    pygame.draw.line(screen, COLOR_SHIFTER_LINE, (cx - (dist_x * 2), cy), (cx + dist_x, cy), 10)
    
    for nome, pos in layout_marchas.items():
        pygame.draw.line(screen, COLOR_SHIFTER_LINE, (pos[0], cy), pos, 10)
        cor = COLOR_GEAR_ACTIVE if nome == marcha_atual else COLOR_TEXT
        pygame.draw.circle(screen, COLOR_BG, pos, 25)
        pygame.draw.circle(screen, cor, pos, 25, 2)
        txt = font_medium.render(nome, True, cor)
        screen.blit(txt, txt.get_rect(center=pos))
            
    pos_manopla = mouse_pos if ctrl_pressionado else shifter_pos_travada
    pygame.draw.circle(screen, COLOR_NEEDLE if ctrl_pressionado else COLOR_GEAR_ACTIVE, pos_manopla, 12)
    
    txt_info1 = font_small.render("Simulador Concept S - V14:", True, COLOR_TEXT_MUTED)
    txt_info2 = font_small.render("1. ESPAÇO: Acelerador | 2. CTRL: Embreagem + Movimento do Mouse | 3. TECLA E: Ignição", True, COLOR_TEXT_MUTED)
    screen.blit(txt_info1, (50, 700))
    screen.blit(txt_info2, (50, 725))
    
    pygame.display.flip()
    clock.tick(60)