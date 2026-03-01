import tkinter as tk
from tkinter import messagebox
import heapq
import random
import time

# Options
BOARD_R = 15
BOARD_C = 15
TILE_W = 35

# Theme: Synthwave Dark
CLR_BG       = "#0f172a"
CLR_SIDE     = "#1e293b"
CLR_GRID     = "#334155"
CLR_TXT      = "#f8fafc"
CLR_MUTED    = "#94a3b8"

CLR_TILE     = "#020617"
CLR_WALL     = "#3b82f6"  # Blue Wall
CLR_SRC      = "#10b981"  # Emerald Start
CLR_TGT      = "#ef4444"  # Red Goal
CLR_OPEN     = "#f59e0b"  # Amber Frontier
CLR_VISITED  = "#8b5cf6"  # Violet Visited
CLR_ROUTE    = "#2dd4bf"  # Teal Path
CLR_BOT      = "#f472b6"  # Pink Agent

# Global State
blocks = set()
src_node = (0, 0)
tgt_node = (BOARD_R - 1, BOARD_C - 1)
running = False
tool_type = "wall"

rec_steps = []
best_route = []

stat_exp = 0
stat_cst = 0
stat_tms = 0.0

# Render tile
def paint_tile(r, c, clr):
    lbl = f"cell_{r}_{c}"
    canvas.delete(lbl)
    x1, y1 = c * TILE_W, r * TILE_W
    x2, y2 = x1 + TILE_W, y1 + TILE_W
    canvas.create_rectangle(x1, y1, x2, y2, fill=clr, outline=CLR_GRID, width=1, tags=lbl)
    
    # Label S/G
    if (r, c) == src_node:
        canvas.create_text(x1 + TILE_W//2, y1 + TILE_W//2, text="S", font=("Consolas", 12, "bold"), fill="white", tags=lbl)
    elif (r, c) == tgt_node:
        canvas.create_text(x1 + TILE_W//2, y1 + TILE_W//2, text="G", font=("Consolas", 12, "bold"), fill="white", tags=lbl)

# Redraw grid
def draw_board():
    canvas.delete("all")
    for r in range(BOARD_R):
        for c in range(BOARD_C):
            if (r, c) == src_node: paint_tile(r, c, CLR_SRC)
            elif (r, c) == tgt_node: paint_tile(r, c, CLR_TGT)
            elif (r, c) in blocks: paint_tile(r, c, CLR_WALL)
            else: paint_tile(r, c, CLR_TILE)

# Process mouse
def handle_click(e):
    if running: return
    c, r = e.x // TILE_W, e.y // TILE_W
    if not (0 <= r < BOARD_R and 0 <= c < BOARD_C): return
    apply_tool(r, c)

def handle_drag(e):
    if tool_type == "wall": handle_click(e)

# Apply cursor tool
def apply_tool(r, c):
    global src_node, tgt_node
    pos = (r, c)
    if tool_type == "start" and pos != tgt_node and pos not in blocks:
        old = src_node
        src_node = pos
        paint_tile(old[0], old[1], CLR_TILE)
        paint_tile(r, c, CLR_SRC)
    elif tool_type == "goal" and pos != src_node and pos not in blocks:
        old = tgt_node
        tgt_node = pos
        paint_tile(old[0], old[1], CLR_TILE)
        paint_tile(r, c, CLR_TGT)
    elif tool_type == "wall" and pos not in (src_node, tgt_node):
        if pos in blocks:
            blocks.remove(pos)
            paint_tile(r, c, CLR_TILE)
        else:
            blocks.add(pos)
            paint_tile(r, c, CLR_WALL)

# Select tool
def set_tool(t):
    global tool_type
    tool_type = t
    for b in [btn_w, btn_s, btn_g]: b.config(bg=CLR_SIDE, fg=CLR_TXT)
    if t == "wall": btn_w.config(bg=CLR_WALL, fg="black")
    elif t == "start": btn_s.config(bg=CLR_SRC, fg="black")
    elif t == "goal": btn_g.config(bg=CLR_TGT, fg="black")

# Generate map
def spawn_maze():
    global blocks
    blocks.clear()
    chance = scale_prob.get() / 100.0
    for r in range(BOARD_R):
        for c in range(BOARD_C):
            if (r, c) in (src_node, tgt_node): continue
            if random.random() < chance:
                blocks.add((r, c))
    draw_board()
    txt_sys.set(">>> Maze Built")

# Clear map
def wipe_walls():
    blocks.clear()
    draw_board()
    txt_sys.set(">>> Walls Purged")

# Heuristics
def measure_h(p1, p2):
    ht = var_heur.get()
    if ht == "Manhattan": return abs(p1[0]-p2[0]) + abs(p1[1]-p2[1])
    return ((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)**0.5

# Adjacent nodes
def get_adj(r, c):
    res = []
    for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)]:
        nr, nc = r+dr, c+dc
        if 0 <= nr < BOARD_R and 0 <= nc < BOARD_C and (nr, nc) not in blocks:
            res.append((nr, nc))
    return res

# Unified Search
def compute_path(s, g):
    start_t = time.perf_counter()
    track_steps = []
    parents = {s: None}
    seen = set()
    expanded = 0
    is_astar = (var_algo.get() == "A*")
    
    if is_astar:
        costs = {s: 0.0}
        q = [(measure_h(s, g), 0.0, s)]
    else:
        q = [(measure_h(s, g), s)]
    
    while q:
        item = heapq.heappop(q)
        if is_astar:
            curr = item[2]
            cst = item[1]
        else:
            curr = item[1]
            cst = 0
            
        if curr in seen: continue
        seen.add(curr)
        expanded += 1
        track_steps.append((curr[0], curr[1], "V"))
        
        # Route found
        if curr == g:
            route = []
            node = g
            while node:
                route.append(node)
                node = parents[node]
            route.reverse()
            return route, track_steps, expanded, (time.perf_counter() - start_t) * 1000
            
        for nb in get_adj(curr[0], curr[1]):
            if is_astar:
                # Actual cost
                ncost = cst + 1
                if nb not in costs or ncost < costs[nb]:
                    costs[nb] = ncost
                    parents[nb] = curr
                    heapq.heappush(q, (ncost + measure_h(nb, g), ncost, nb))
                    track_steps.append((nb[0], nb[1], "F"))
            else:
                # Heuristic only
                if nb not in seen and nb not in parents:
                    parents[nb] = curr
                    heapq.heappush(q, (measure_h(nb, g), nb))
                    track_steps.append((nb[0], nb[1], "F"))
                    
    return None, track_steps, expanded, (time.perf_counter() - start_t) * 1000

# Scanner trigger
def begin_scan():
    global running, rec_steps, best_route, stat_exp, stat_cst, stat_tms
    if running: return
    clean_paths()
    running = True
    txt_sys.set(f">>> Executing {var_algo.get()}")
    
    route, steps, exp, tms = compute_path(src_node, tgt_node)
    stat_exp = exp
    stat_tms = tms
    rec_steps = steps
    
    if route:
        best_route = route
        stat_cst = len(route) - 1
    else:
        best_route = []
        stat_cst = 0
        
    refresh_stats()
    playback_scan(0)

# Animator
def playback_scan(i):
    global running
    if not running: return
    
    for _ in range(5):
        if i >= len(rec_steps):
            display_route()
            return
        r, c, v_type = rec_steps[i]
        if (r, c) not in (src_node, tgt_node):
            paint_tile(r, c, CLR_VISITED if v_type == "V" else CLR_OPEN)
        i += 1
    
    root.update_idletasks()
    root.after(30, lambda: playback_scan(i))

# Trace back paths
def display_route():
    global running
    if not best_route:
        txt_sys.set(">>> FAILED. NO PATH.")
        messagebox.showwarning("Error", "Target Unreachable")
        running = False
        return
        
    if var_dyn.get():
        for n in best_route[1:-1]: paint_tile(n[0], n[1], CLR_ROUTE)
        walk_agent(0, list(best_route))
    else:
        for n in best_route[1:-1]: paint_tile(n[0], n[1], CLR_ROUTE)
        txt_sys.set(">>> COMPLETE.")
        running = False

# Dynamic tracking
def walk_agent(step, active_path):
    global running, stat_exp, stat_cst, stat_tms
    if not running: return
    
    if step >= len(active_path):
        txt_sys.set(">>> SECURED.")
        running = False
        return
        
    bot_pos = active_path[step]
    
    # Random anomaly
    if random.random() < 0.10:
        new_b = drop_block(bot_pos)
        if new_b and new_b in active_path[step:]:
            txt_sys.set(">>> OBSTRUCTION! Recalculating...")
            clean_paths()
            nr, stp, ex, tm = compute_path(bot_pos, tgt_node)
            stat_exp += ex
            stat_tms += tm
            if not nr:
                txt_sys.set(">>> DEAD END.")
                running = False
                return
            stat_cst += len(nr) - 1
            refresh_stats()
            for n in nr[1:-1]: paint_tile(n[0], n[1], CLR_ROUTE)
            active_path = nr
            step = 0
            bot_pos = active_path[0]
            
    if bot_pos not in (src_node, tgt_node): paint_tile(bot_pos[0], bot_pos[1], CLR_BOT)
    if step > 0:
        prv = active_path[step-1]
        if prv not in (src_node, tgt_node): paint_tile(prv[0], prv[1], CLR_ROUTE)
        
    root.update_idletasks()
    root.after(150, lambda: walk_agent(step+1, active_path))

# Dynamic blocks
def drop_block(avoid):
    for _ in range(20):
        r, c = random.randint(0, BOARD_R-1), random.randint(0, BOARD_C-1)
        if (r, c) not in (src_node, tgt_node, avoid) and (r, c) not in blocks:
            blocks.add((r, c))
            paint_tile(r, c, CLR_WALL)
            return (r, c)
    return None

# Clean UI layers
def clean_paths():
    for r in range(BOARD_R):
        for c in range(BOARD_C):
            if (r, c) not in (src_node, tgt_node) and (r, c) not in blocks:
                paint_tile(r, c, CLR_TILE)

def halt_scan():
    global running
    running = False
    txt_sys.set(">>> HALTED")

def factory_reset():
    global running, stat_exp, stat_cst, stat_tms
    running = False
    stat_exp, stat_cst, stat_tms = 0, 0, 0.0
    refresh_stats()
    draw_board()
    txt_sys.set(">>> SYSTEM READY")

def refresh_stats():
    l_exp.config(text=str(stat_exp))
    l_cst.config(text=str(stat_cst))
    l_tms.config(text=f"{stat_tms:.1f}")

# GUI Init
root = tk.Tk()
root.title("Nexus Path AI")
root.geometry("1000x680")
root.config(bg=CLR_BG)

panel = tk.Frame(root, bg=CLR_SIDE, width=220, padx=10, pady=10)
panel.pack(side="left", fill="y")
panel.pack_propagate(False)

tk.Label(panel, text="NEXUS DIR", bg=CLR_SIDE, fg=CLR_TXT, font=("Consolas", 14, "bold")).pack()
tk.Frame(panel, bg=CLR_GRID, height=1).pack(fill="x", pady=10)

tk.Label(panel, text="PROTOCOL", bg=CLR_SIDE, fg=CLR_MUTED, font=("Consolas", 8)).pack(anchor="w")
var_algo = tk.StringVar(value="A*")
tk.Radiobutton(panel, text="A* Search", variable=var_algo, value="A*", bg=CLR_SIDE, fg=CLR_TXT, selectcolor=CLR_BG, activebackground=CLR_SIDE).pack(anchor="w")
tk.Radiobutton(panel, text="Greedy (GBFS)", variable=var_algo, value="GBFS", bg=CLR_SIDE, fg=CLR_TXT, selectcolor=CLR_BG, activebackground=CLR_SIDE).pack(anchor="w")

tk.Label(panel, text="HEURISTIC", bg=CLR_SIDE, fg=CLR_MUTED, font=("Consolas", 8)).pack(anchor="w", pady=(10,0))
var_heur = tk.StringVar(value="Manhattan")
tk.Radiobutton(panel, text="Manhattan", variable=var_heur, value="Manhattan", bg=CLR_SIDE, fg=CLR_TXT, selectcolor=CLR_BG, activebackground=CLR_SIDE).pack(anchor="w")
tk.Radiobutton(panel, text="Euclidean", variable=var_heur, value="Euclidean", bg=CLR_SIDE, fg=CLR_TXT, selectcolor=CLR_BG, activebackground=CLR_SIDE).pack(anchor="w")

tk.Label(panel, text="CURSOR TOOL", bg=CLR_SIDE, fg=CLR_MUTED, font=("Consolas", 8)).pack(anchor="w", pady=(10,0))
tr = tk.Frame(panel, bg=CLR_SIDE)
tr.pack(fill="x", pady=2)
btn_w = tk.Button(tr, text="Wall", bg=CLR_WALL, fg="black", command=lambda: set_tool("wall"), font=("Consolas", 8, "bold"))
btn_s = tk.Button(tr, text="Start", bg=CLR_SIDE, fg=CLR_TXT, command=lambda: set_tool("start"), font=("Consolas", 8, "bold"))
btn_g = tk.Button(tr, text="Goal", bg=CLR_SIDE, fg=CLR_TXT, command=lambda: set_tool("goal"), font=("Consolas", 8, "bold"))
btn_w.pack(side="left", expand=True, fill="x")
btn_s.pack(side="left", expand=True, fill="x")
btn_g.pack(side="left", expand=True, fill="x")

tk.Label(panel, text="DATASCAPE", bg=CLR_SIDE, fg=CLR_MUTED, font=("Consolas", 8)).pack(anchor="w", pady=(10,0))
scale_prob = tk.Scale(panel, from_=10, to=60, orient="horizontal", bg=CLR_SIDE, fg=CLR_TXT, highlightthickness=0, bd=0)
scale_prob.set(25)
scale_prob.pack(fill="x")
tk.Button(panel, text="Seed Random Variables", bg=CLR_BG, fg=CLR_TXT, font=("Consolas", 8), command=spawn_maze).pack(fill="x", pady=2)
tk.Button(panel, text="Format Disk (Clear)", bg=CLR_BG, fg=CLR_TXT, font=("Consolas", 8), command=wipe_walls).pack(fill="x")

tk.Label(panel, text="ENV VARIABLE", bg=CLR_SIDE, fg=CLR_MUTED, font=("Consolas", 8)).pack(anchor="w", pady=(10,0))
var_dyn = tk.BooleanVar(value=False)
tk.Checkbutton(panel, text="Dynamic Hazards", variable=var_dyn, bg=CLR_SIDE, fg=CLR_TXT, selectcolor=CLR_BG, font=("Consolas", 9), activebackground=CLR_SIDE).pack(anchor="w")

tk.Frame(panel, bg=CLR_GRID, height=1).pack(fill="x", pady=15)

tk.Button(panel, text="// COMPILE & RUN", bg=CLR_SRC, fg="black", font=("Consolas", 10, "bold"), command=begin_scan).pack(fill="x")
bx = tk.Frame(panel, bg=CLR_SIDE)
bx.pack(fill="x", pady=2)
tk.Button(bx, text="KILL", bg=CLR_TGT, fg="white", font=("Consolas", 8, "bold"), command=halt_scan).pack(side="left", expand=True, fill="x")
tk.Button(bx, text="RST", bg=CLR_GRID, fg=CLR_TXT, font=("Consolas", 8, "bold"), command=factory_reset).pack(side="left", expand=True, fill="x")

tk.Label(panel, text="TELEMETRY", bg=CLR_SIDE, fg=CLR_MUTED, font=("Consolas", 8)).pack(anchor="w", pady=(10,0))
mbx = tk.Frame(panel, bg=CLR_BG, padx=5, pady=5)
mbx.pack(fill="x")
tk.Label(mbx, text="Nodes:", bg=CLR_BG, fg=CLR_MUTED, font=("Consolas", 8)).grid(row=0, column=0, sticky="w")
l_exp = tk.Label(mbx, text="0", bg=CLR_BG, fg=CLR_OPEN, font=("Consolas", 9, "bold"))
l_exp.grid(row=0, column=1, sticky="e")
tk.Label(mbx, text="Cost:", bg=CLR_BG, fg=CLR_MUTED, font=("Consolas", 8)).grid(row=1, column=0, sticky="w")
l_cst = tk.Label(mbx, text="0", bg=CLR_BG, fg=CLR_OPEN, font=("Consolas", 9, "bold"))
l_cst.grid(row=1, column=1, sticky="e")
tk.Label(mbx, text="Timing:", bg=CLR_BG, fg=CLR_MUTED, font=("Consolas", 8)).grid(row=2, column=0, sticky="w")
l_tms = tk.Label(mbx, text="0.0", bg=CLR_BG, fg=CLR_OPEN, font=("Consolas", 9, "bold"))
l_tms.grid(row=2, column=1, sticky="e")
mbx.columnconfigure(1, weight=1)

txt_sys = tk.StringVar(value=">>> SYSTEM READY")
tk.Label(panel, textvariable=txt_sys, bg=CLR_SIDE, fg=CLR_ROUTE, font=("Consolas", 8, "bold")).pack(pady=10)

c_frame = tk.Frame(root, bg=CLR_BG)
c_frame.pack(side="left", expand=True, fill="both", padx=20, pady=20)

# Center canvas using a pack trick or grid
canvas = tk.Canvas(c_frame, bg=CLR_TILE, bd=0, highlightthickness=1, highlightbackground=CLR_GRID, width=BOARD_C*TILE_W, height=BOARD_R*TILE_W)
canvas.pack(anchor="center", expand=True)

canvas.bind("<Button-1>", handle_click)
canvas.bind("<B1-Motion>", handle_drag)

draw_board()
root.mainloop()