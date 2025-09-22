import js
from pyodide.ffi import create_proxy

"""Browser UI logic (lightweight) – decoupled from core engine for now."""

WIN_PATTERNS = [
    (0,1,2),(3,4,5),(6,7,8),
    (0,3,6),(1,4,7),(2,5,8),
    (0,4,8),(2,4,6)
]

class Metrics:
    def __init__(self):
        self.nodes = 0
        self.cutoffs = 0
    def snapshot(self):
        return {"nodes": self.nodes, "cutoffs": self.cutoffs}

class Game:
    def __init__(self):
        self.cells = [" "] * 9
        self.starting = "X"
        self.current = "X"
        self.game_over = False
        self.winner = None
        self.winning_line = []

    def possible_moves(self):
        return [i for i,c in enumerate(self.cells) if c == " "] if not self.game_over else []

    def apply(self, idx):
        if self.game_over or self.cells[idx] != " ":
            return False
        self.cells[idx] = self.current
        self._update_state()
        if not self.game_over:
            self.current = ("O" if self.current == "X" else "X")
        return True

    def _update_state(self):
        for a,b,c in WIN_PATTERNS:
            trio = self.cells[a], self.cells[b], self.cells[c]
            if trio[0] != " " and trio[0] == trio[1] == trio[2]:
                self.game_over = True
                self.winner = trio[0]
                self.winning_line = [a,b,c]
                return
        if all(c != " " for c in self.cells):
            self.game_over = True

    def score(self, mark):
        if not self.game_over:
            return None
        if self.winner is None:
            return 0
        return 1 if self.winner == mark else -1


def minimax(game: Game, mark: str, maximizing: bool, depth_limit: int | None = None, metrics: Metrics | None = None, alpha: float | None = None, beta: float | None = None):
    if metrics is None:
        metrics = Metrics()
    metrics.nodes += 1
    if game.game_over:
        return game.score(mark), None, metrics
    if depth_limit is not None and depth_limit <= 0:
        # Simple heuristic evaluation
        score = 0.0
        center = 4
        if game.cells[center] == mark:
            score += 0.2
        elif game.cells[center] == mark_other(mark):
            score -= 0.2
        corners = [0,2,6,8]
        own_corners = sum(1 for i in corners if game.cells[i] == mark)
        opp_corners = sum(1 for i in corners if game.cells[i] == mark_other(mark))
        score += 0.05 * (own_corners - opp_corners)
        return score, None, metrics
    moves = game.possible_moves()
    def ordering(i):
        if i == 4: return 0
        if i in (0,2,6,8): return 1
        return 2
    moves.sort(key=ordering)
    best_score = float('-inf') if maximizing else float('inf')
    best_move = None
    local_alpha = -1e9 if alpha is None else alpha
    local_beta = 1e9 if beta is None else beta
    for m in moves:
        new_g = clone(game)
        new_g.apply(m)
        score,_,_ = minimax(new_g, mark, new_g.current == mark, None if depth_limit is None else depth_limit - 1, metrics, local_alpha, local_beta)
        if maximizing:
            if score > best_score:
                best_score, best_move = score, m
            local_alpha = max(local_alpha, best_score)
        else:
            if score < best_score:
                best_score, best_move = score, m
            local_beta = min(local_beta, best_score)
        if local_beta <= local_alpha:
            metrics.cutoffs += 1
            break
    return best_score, best_move, metrics

def mark_other(mark: str) -> str:
    return 'O' if mark == 'X' else 'X'


def clone(game: Game) -> Game:
    g = Game()
    g.cells = game.cells.copy()
    g.starting = game.starting
    g.current = game.current
    g.game_over = game.game_over
    g.winner = game.winner
    g.winning_line = game.winning_line.copy()
    return g

class UI:
    def __init__(self):
        self.game = Game()
        self.board_el = js.document.getElementById("board")
        self.status_el = js.document.getElementById("status")
        self.analysis_el = js.document.getElementById("analysis")
        self.reveal_analysis = False
        self.live_region = self.ensure_live_region()
        self.difficulty = 'hard'
        self.last_metrics = None
        self.tree_container = None
        self.tree_root = None
        self.tree_flat = []  # linear evaluation order
        self.step_index = -1
        self.build_board()
        self.bind_controls()
        self.restore_theme()
        self.render()

    def bind_controls(self):
        js.document.getElementById("new-game").addEventListener("click", create_proxy(self.on_new))
        js.document.getElementById("toggle-theme").addEventListener("click", create_proxy(self.on_theme))
        js.document.getElementById("toggle-visuals").addEventListener("click", create_proxy(self.on_toggle_visuals))
        js.document.getElementById("difficulty").addEventListener("change", create_proxy(self.on_difficulty))
        js.document.addEventListener("keydown", create_proxy(self.on_key))
        expand_btn = js.document.getElementById("expand-tree")
        step_btn = js.document.getElementById("step-tree")
        export_btn = js.document.getElementById("export-tree")
        if expand_btn:
            expand_btn.addEventListener("click", create_proxy(self.on_toggle_tree))
        if step_btn:
            step_btn.addEventListener("click", create_proxy(self.on_step))
        if export_btn:
            export_btn.addEventListener("click", create_proxy(self.on_export_tree))
        self.tree_container = js.document.getElementById("tree")

    def ensure_live_region(self):
        el = js.document.getElementById("live-region")
        if not el:
            el = js.document.createElement('div')
            el.id = 'live-region'
            el.setAttribute('role','status')
            el.setAttribute('aria-live','polite')
            js.document.body.appendChild(el)
        return el

    def on_new(self, evt=None):
        self.game = Game()
        self.render()
        self.announce("New game started. X to move.")
        self.clear_tree_state()

    def on_theme(self, evt=None):
        root = js.document.documentElement
        theme = root.getAttribute('data-theme')
        new_theme = 'dark' if theme == 'light' else 'light'
        root.setAttribute('data-theme', new_theme)
        try:
            js.window.localStorage.setItem('ttt-theme', new_theme)
        except Exception:
            pass
        btn = js.document.getElementById('toggle-theme')
        if btn:
            btn.setAttribute('aria-label', f"Switch to {'light' if new_theme=='dark' else 'dark'} mode")
        self.announce(f"Theme switched to {new_theme} mode")

    def on_toggle_visuals(self, evt=None):
        btn = js.document.getElementById("toggle-visuals")
        pressed = btn.getAttribute('aria-pressed') == 'true'
        btn.setAttribute('aria-pressed', 'false' if pressed else 'true')
        self.reveal_analysis = not pressed
        self.render()
        if self.reveal_analysis:
            self.build_tree()
        else:
            self.clear_tree()
        btn.setAttribute('aria-label', 'Hide AI reasoning' if self.reveal_analysis else 'Show AI reasoning')
        self.announce('AI reasoning enabled' if self.reveal_analysis else 'AI reasoning disabled')

    def on_difficulty(self, evt=None):
        sel = js.document.getElementById('difficulty').value
        self.difficulty = sel
        self.render()
        self.announce(f"Difficulty set to {sel.capitalize()}")

    def build_board(self):
        self.board_el.innerHTML = ''
        for i in range(9):
            cell = js.document.createElement('button')
            cell.className = 'cell'
            cell.setAttribute('role','gridcell')
            cell.setAttribute('data-idx', str(i))
            cell.setAttribute('tabindex', '0')
            cell.setAttribute('aria-label', f"Cell {i+1}")
            cell.addEventListener('click', create_proxy(lambda e, idx=i: self.on_cell(idx)))
            self.board_el.appendChild(cell)

    def on_key(self, evt):
        # Arrow key board navigation
        key = evt.key
        focus = js.document.activeElement
        if not focus or 'cell' not in focus.className:
            return
        idx = int(focus.getAttribute('data-idx'))
        moves = {'ArrowRight': 1, 'ArrowLeft': -1, 'ArrowUp': -3, 'ArrowDown': 3}
        if key in moves:
            evt.preventDefault()
            new_idx = idx + moves[key]
            if 0 <= new_idx < 9:
                target = self.board_el.children.item(new_idx)
                if target:
                    target.focus()
        elif key in ('Enter', ' '):
            evt.preventDefault()
            self.on_cell(idx)

    def on_cell(self, idx):
        if self.game.game_over:
            return
        if self.game.current == 'O':
            # Prevent clicking during AI turn
            return
        moved = self.game.apply(idx)
        if moved:
            self.render()
            self.ai_move_if_needed()
            self.announce(f"Placed {self.game.cells[idx]} in cell {idx+1}")
        else:
            self.announce("Invalid move")

    def ai_move_if_needed(self):
        if self.game.game_over:
            return
        if self.game.current == 'O':
            move = self.choose_ai_move()
            if move is not None:
                self.game.apply(move)
                self.render()
                self.announce(f"AI played in cell {move+1}")
                if self.reveal_analysis:
                    self.build_tree()

    def compute_scores(self):
        scores = {}
        if self.game.game_over:
            return scores
        for m in self.game.possible_moves():
            new_g = clone(self.game)
            new_g.apply(m)
            depth_limit, use_ab = self.depth_config()
            metrics = Metrics()
            score,_,_ = minimax(new_g, self.game.current, new_g.current == self.game.current, depth_limit, metrics, None if not use_ab else -1e9, None if not use_ab else 1e9)
            scores[m] = score
        return scores

    def render(self):
        # Update status
        # Reset status classes
        for cls in ("win","loss","tie"):
            self.status_el.classList.remove(cls)
        if self.game.game_over:
            if self.game.winner:
                self.status_el.textContent = f"Winner: {self.game.winner}"
                if self.game.winner == 'X':
                    self.status_el.classList.add("win")
                else:
                    # Human is assumed X; show loss color when AI (O) wins
                    self.status_el.classList.add("loss")
                self.announce(f"Game over. {self.game.winner} wins.")
            else:
                self.status_el.textContent = "Tie Game"
                self.status_el.classList.add("tie")
                self.announce("Game over. Tie.")
        else:
            self.status_el.textContent = f"Turn: {self.game.current}"

        scores = self.compute_scores() if self.reveal_analysis else {}
        for i, cell in enumerate(self.board_el.children):
            mark = self.game.cells[i]
            cell.textContent = mark if mark != ' ' else ''
            if i in self.game.winning_line:
                cell.setAttribute('data-winning', 'true')
            else:
                cell.removeAttribute('data-winning')
            # Add placement animation
            if mark != ' ' and 'played' not in cell.classList.toString():
                cell.classList.add('played')
            if self.reveal_analysis and (not self.game.game_over) and self.game.cells[i] == ' ':
                score = scores.get(i)
                if score is not None:
                    cell.setAttribute('data-score', str(score))
                    if score == 1:
                        cell.setAttribute('data-outcome','win')
                    elif score == 0:
                        cell.setAttribute('data-outcome','tie')
                    else:
                        cell.setAttribute('data-outcome','loss')
                else:
                    cell.removeAttribute('data-score')
            else:
                cell.removeAttribute('data-score')
                if not self.game.game_over:
                    cell.removeAttribute('data-outcome')

        # For terminal board show outcome halo for winning line or all cells on tie
        if self.game.game_over:
            if self.game.winner:
                for i, cell in enumerate(self.board_el.children):
                    if i in self.game.winning_line:
                        cell.setAttribute('data-outcome','win')
            else:
                for cell in self.board_el.children:
                    cell.setAttribute('data-outcome','tie')

        if self.reveal_analysis and not self.game.game_over:
            self.analysis_el.innerHTML = self.render_analysis(scores)
        elif self.game.game_over:
            self.analysis_el.innerHTML = "Game over. Start a new game to analyze fresh positions."
        else:
            self.analysis_el.innerHTML = "Enable reasoning (🧠) to view minimax scores."
        if self.reveal_analysis and self.tree_container:
            # ensure tree built
            if not self.tree_root:
                self.build_tree()

    def render_analysis(self, scores):
        if not scores:
            return "No available moves." if self.game.game_over else "Computing..."
        items = []
        for idx, score in sorted(scores.items()):
            items.append(f"<li>Cell {idx+1}: score {round(score,3)}</li>")
        metrics_line = ''
        if self.last_metrics:
            metrics_line = f"<p class='metrics'>Nodes: {self.last_metrics['nodes']} Cutoffs: {self.last_metrics['cutoffs']}</p>"
        return f"<ul class='scores'>{''.join(items)}</ul>{metrics_line}"

    # ---------- Tree Visualization ----------
    def build_tree(self):
        self.clear_tree_state()
        depth_limit, use_ab = self.depth_config()
        heuristics = depth_limit is not None
        # Build full tree (respect depth limit for visualization consistency)
        metrics = Metrics()
        self.tree_root = self.expand_node(self.game, self.game.current, heuristics, depth_limit, use_ab, metrics)
        self.tree_flat = []
        self.linearize(self.tree_root)
        self.render_tree()
        self.step_index = -1

    def expand_node(self, game: Game, turn: str, heuristics: bool, depth_limit, use_ab, metrics: Metrics, alpha=-1e9, beta=1e9):
        node = {
            'board': ''.join(game.cells),
            'turn': turn,
            'children': [],
            'score': None,
            'terminal': game.game_over,
            'pruned': False,
            'type': None,
        }
        metrics.nodes += 1
        if game.game_over:
            node['score'] = game.score(self.game.current)
            node['type'] = self.score_type(node['score'])
            return node
        if heuristics and depth_limit == 0:
            # heuristic evaluation mimic
            score = 0.0
            if game.cells[4] == self.game.current:
                score += 0.2
            corners = [0,2,6,8]
            own = sum(1 for i in corners if game.cells[i] == self.game.current)
            opp = sum(1 for i in corners if game.cells[i] == mark_other(self.game.current))
            score += 0.05 * (own - opp)
            node['score'] = score
            node['type'] = 'heuristic'
            return node
        moves = game.possible_moves()
        def ordering(i):
            if i == 4: return 0
            if i in (0,2,6,8): return 1
            return 2
        moves.sort(key=ordering)
        maximizing = (turn == self.game.current)
        best_score = float('-inf') if maximizing else float('inf')
        for m in moves:
            new_g = clone(game)
            new_g.apply(m)
            child = self.expand_node(new_g, new_g.current, heuristics, None if depth_limit is None else depth_limit - 1, use_ab, metrics, alpha, beta)
            node['children'].append({'move': m, 'node': child})
            sc = child['score']
            if sc is not None:
                if maximizing and sc > best_score:
                    best_score = sc
                if not maximizing and sc < best_score:
                    best_score = sc
            if use_ab and sc is not None:
                if maximizing:
                    if sc > alpha: alpha = sc
                else:
                    if sc < beta: beta = sc
                if beta <= alpha:
                    metrics.cutoffs += 1
                    # mark remaining as pruned
                    remaining = moves[moves.index(m)+1:]
                    for rm in remaining:
                        node['children'].append({'move': rm, 'node': {'board': '', 'turn': turn, 'children': [], 'score': None, 'terminal': False, 'pruned': True, 'type': 'pruned'}})
                    break
        node['score'] = best_score if best_score != float('-inf') and best_score != float('inf') else 0
        node['type'] = self.score_type(node['score']) if node['type'] is None else node['type']
        return node

    def score_type(self, score):
        if isinstance(score, float) and not score.is_integer():
            return 'heuristic'
        if score == 1:
            return 'win'
        if score == -1:
            return 'loss'
        if score == 0:
            return 'tie'
        return 'heuristic'

    def linearize(self, node):
        self.tree_flat.append(node)
        for child in node.get('children', []):
            self.linearize(child['node'])

    def clear_tree_state(self):
        self.tree_root = None
        self.tree_flat = []
        self.step_index = -1
        if self.tree_container:
            self.tree_container.innerHTML = ''

    def clear_tree(self):
        self.clear_tree_state()
        if self.tree_container:
            self.tree_container.setAttribute('hidden','')
        btn = js.document.getElementById('expand-tree')
        if btn:
            btn.setAttribute('aria-pressed','false')

    def on_toggle_tree(self, evt=None):
        btn = js.document.getElementById('expand-tree')
        if not self.tree_container or not btn:
            return
        pressed = btn.getAttribute('aria-pressed') == 'true'
        if pressed:
            btn.setAttribute('aria-pressed','false')
            self.tree_container.setAttribute('hidden','')
        else:
            btn.setAttribute('aria-pressed','true')
            self.tree_container.removeAttribute('hidden')
            if not self.tree_root:
                self.build_tree()
        btn.setAttribute('aria-label', 'Show minimax tree' if pressed else 'Hide minimax tree')
        self.announce('Tree hidden' if pressed else 'Tree shown')

    def on_step(self, evt=None):
        if not self.tree_root:
            self.build_tree()
        if self.step_index + 1 < len(self.tree_flat):
            self.step_index += 1
            node = self.tree_flat[self.step_index]
            # highlight board cells for node (if board present)
            if node.get('board') and len(node['board']) == 9:
                self.highlight_board_from_string(node['board'])
            self.announce(f"Step {self.step_index+1} / {len(self.tree_flat)}")
        else:
            self.announce('End of traversal')
        btn = js.document.getElementById('step-tree')
        if btn:
            btn.setAttribute('aria-label', f"Traversal step {self.step_index+1} of {len(self.tree_flat)}" if self.step_index >= 0 else 'Traversal start')

    def on_export_tree(self, evt=None):
        if not self.tree_root:
            self.build_tree()
        import json
        data = json.dumps(self.tree_root)
        try:
            promise = js.navigator.clipboard.writeText(data)
            # Attach then/catch to surface success/fallback
            def on_success(_=None):
                self.announce('Tree JSON copied to clipboard')
            def on_failure(err=None):
                self.show_export_fallback(data)
                self.announce('Clipboard unavailable. Fallback shown.')
            promise.then(create_proxy(on_success)).catch(create_proxy(on_failure))
        except Exception:
            self.show_export_fallback(data)
            self.announce('Clipboard blocked. Manual copy required.')

    def show_export_fallback(self, data: str):
        existing = js.document.getElementById('export-fallback')
        if existing:
            existing.parentElement.removeChild(existing)
        overlay = js.document.createElement('div')
        overlay.id = 'export-fallback'
        overlay.className = 'export-fallback fade-in'
        inner = js.document.createElement('div')
        inner.className = 'export-fallback-inner'
        title = js.document.createElement('h3')
        title.textContent = 'Export Tree JSON'
        para = js.document.createElement('p')
        para.textContent = 'Clipboard access was denied. Select and copy manually.'
        ta = js.document.createElement('textarea')
        ta.value = data
        ta.setAttribute('readonly','')
        ta.addEventListener('focus', create_proxy(lambda e: ta.select()))
        actions = js.document.createElement('div')
        actions.className = 'export-actions'
        close_btn = js.document.createElement('button')
        close_btn.className = 'btn'
        close_btn.textContent = 'Close'
        def close(_=None):
            if overlay.parentElement:
                overlay.parentElement.removeChild(overlay)
        close_btn.addEventListener('click', create_proxy(close))
        copy_btn = js.document.createElement('button')
        copy_btn.className = 'btn btn-primary'
        copy_btn.textContent = 'Copy'
        def manual_copy(_=None):
            try:
                ta.select()
                js.document.execCommand('copy')
                self.announce('Copied!')
            except Exception:
                self.announce('Select text and press Ctrl+C')
        copy_btn.addEventListener('click', create_proxy(manual_copy))
        actions.appendChild(copy_btn)
        actions.appendChild(close_btn)
        inner.appendChild(title)
        inner.appendChild(para)
        inner.appendChild(ta)
        inner.appendChild(actions)
        overlay.appendChild(inner)
        js.document.body.appendChild(overlay)

    def highlight_board_from_string(self, board_str: str):
        for i, cell in enumerate(self.board_el.children):
            ch = board_str[i]
            # temporary overlay via outline
            if ch == 'X' or ch == 'O':
                cell.style.outline = '2px solid var(--accent)'
            else:
                cell.style.outline = ''
        js.setTimeout(create_proxy(lambda : self.clear_highlights()), 650)

    def clear_highlights(self):
        for cell in self.board_el.children:
            cell.style.outline = ''

    def render_tree(self):
        if not self.tree_container or not self.tree_root:
            return
        self.tree_container.innerHTML = ''
        root_ul = js.document.createElement('ul')
        root_ul.appendChild(self.render_tree_node(self.tree_root))
        self.tree_container.appendChild(root_ul)

    def render_tree_node(self, node):
        li = js.document.createElement('li')
        btn = js.document.createElement('div')
        btn.className = 'node'
        if node.get('type'):
            btn.classList.add(node['type'])
        if node.get('pruned'):
            btn.classList.add('pruned')
        score = node.get('score')
        btn.innerHTML = f"<span class='score'>{'' if score is None else round(score,3)}</span> <code>{node.get('board','') or '…'}</code>"
        btn.setAttribute('data-expanded','false')
        btn.addEventListener('click', create_proxy(lambda e, n=node, b=btn: self.toggle_expand(n, b)))
        li.appendChild(btn)
        return li

    def toggle_expand(self, node, btn):
        expanded = btn.getAttribute('data-expanded') == 'true'
        if expanded:
            btn.setAttribute('data-expanded','false')
            # remove children list
            if btn.nextSibling:
                btn.parentElement.removeChild(btn.nextSibling)
        else:
            btn.setAttribute('data-expanded','true')
            if node.get('children'):
                ul = js.document.createElement('ul')
                for child in node['children']:
                    ul.appendChild(self.render_tree_node(child['node']))
                btn.parentElement.appendChild(ul)

    def choose_ai_move(self):
        moves = self.game.possible_moves()
        if not moves:
            return None
        if self.difficulty == 'random':
            from random import choice
            return choice(moves)
        depth_limit, use_ab = self.depth_config()
        best_move = None
        best_score = float('-inf')
        metrics = Metrics()
        for m in moves:
            new_g = clone(self.game)
            new_g.apply(m)
            score,_,_ = minimax(new_g, 'O', new_g.current == 'O', depth_limit, metrics, None if not use_ab else -1e9, None if not use_ab else 1e9)
            if score > best_score:
                best_score = score
                best_move = m
        self.last_metrics = metrics.snapshot()
        return best_move

    def depth_config(self):
        if self.difficulty == 'normal':
            return 3, False
        if self.difficulty == 'hard':
            return None, False
        if self.difficulty == 'expert':
            return None, True
        if self.difficulty == 'random':
            return 0, False
        return None, False

    def announce(self, message: str):
        # Update live region for screen readers
        self.live_region.textContent = message

    def restore_theme(self):
        try:
            stored = js.window.localStorage.getItem('ttt-theme')
            if stored:
                js.document.documentElement.setAttribute('data-theme', stored)
        except Exception:
            pass


def main():
    import traceback
    try:
        UI()
    except Exception as exc:  # pragma: no cover - runtime surface
        # Surface traceback to page for easier debugging
        pre = js.document.createElement('pre')
        pre.style.whiteSpace = 'pre-wrap'
        pre.style.background = '#330'
        pre.style.color = '#fff'
        pre.style.padding = '1rem'
        pre.textContent = 'Initialization error:\n' + traceback.format_exc()
        js.document.body.appendChild(pre)
        status_el = js.document.getElementById('status')
        if status_el:
            status_el.textContent = 'Error during initialization.'

main()
