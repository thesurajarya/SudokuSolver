import pygame
import sys
import random
import networkx as nx

def print_sudoku(grid):
    """Prints the Sudoku grid in a readable format."""
    for row in grid:
        print(" ".join(str(num) if num != 0 else '.' for num in row))
    print()

def build_sudoku_graph():
    """Builds a graph representation of the Sudoku puzzle."""
    G = nx.Graph()

    # Add nodes for each cell
    for i in range(9):
        for j in range(9):
            G.add_node((i, j))

    # Add edges for rows and columns
    for i in range(9):
        for j in range(9):
            for k in range(j + 1, 9):
                G.add_edge((i, j), (i, k))  # Same row
                G.add_edge((j, i), (k, i))  # Same column

    # Add edges for 3x3 subgrids
    for box_row in range(3):
        for box_col in range(3):
            cells = [
                (box_row * 3 + i, box_col * 3 + j)
                for i in range(3) for j in range(3)
            ]
            for m in range(len(cells)):
                for n in range(m + 1, len(cells)):
                    G.add_edge(cells[m], cells[n])

    return G

def solve_sudoku_with_graph(grid):
    """Solves the Sudoku puzzle using graph coloring."""
    G = build_sudoku_graph()

    # Assign initial colors (numbers) to nodes based on the grid
    colors = {}
    for i in range(9):
        for j in range(9):
            if grid[i][j] != 0:
                colors[(i, j)] = grid[i][j]

    # Define possible colors (numbers 1-9)
    possible_colors = {i for i in range(1, 10)}

    # Try to color the graph
    def is_valid_coloring(node, color):
        for neighbor in G.neighbors(node):
            if neighbor in colors and colors[neighbor] == color:
                return False
        return True

    def backtrack(node_index):
        if node_index == len(G.nodes):
            return True

        node = list(G.nodes)[node_index]
        if node in colors:  # Skip pre-filled nodes
            return backtrack(node_index + 1)

        for color in possible_colors:
            if is_valid_coloring(node, color):
                colors[node] = color
                if backtrack(node_index + 1):
                    return True
                del colors[node]

        return False

    if backtrack(0):
        for (i, j), value in colors.items():
            grid[i][j] = value
        return True

    return False

def draw_grid(screen, grid, font):
    """Draws the Sudoku grid on the screen."""
    screen.fill((255, 255, 255))  # White background
    for i in range(10):
        width = 3 if i % 3 == 0 else 1
        pygame.draw.line(screen, (0, 0, 0), (50 + i * 50, 50), (50 + i * 50, 500), width)
        pygame.draw.line(screen, (0, 0, 0), (50, 50 + i * 50), (500, 50 + i * 50), width)

    for i in range(9):
        for j in range(9):
            if grid[i][j] != 0:
                text = font.render(str(grid[i][j]), True, (0, 0, 0))
                screen.blit(text, (65 + j * 50, 55 + i * 50))

def generate_random_sudoku():
    """Generates a random Sudoku puzzle."""
    base_grid = [[0] * 9 for _ in range(9)]
    solve_sudoku_with_graph(base_grid)  # Fill the grid

    # Remove some numbers to create a puzzle
    for _ in range(random.randint(40, 50)):
        i, j = random.randint(0, 8), random.randint(0, 8)
        base_grid[i][j] = 0

    return base_grid

def get_hint(grid, solved_grid):
    """Provides a hint by returning the first empty cell's value from the solved grid."""
    for i in range(9):
        for j in range(9):
            if grid[i][j] == 0:
                return i, j, solved_grid[i][j]
    return None

def draw_graph_update(graph_info, font, screen):
    """Displays graph theory updates in a separate window."""
    info_surface = pygame.Surface((500, 600))
    info_surface.fill((200, 200, 200))  # Light gray background
    y_offset = 10
    for info in graph_info:
        text = font.render(info, True, (0, 0, 0))
        info_surface.blit(text, (10, y_offset))
        y_offset += 30
    screen.blit(info_surface, (550, 0))

def main():
    pygame.init()
    screen = pygame.display.set_mode((1100, 600))
    pygame.display.set_caption("Sudoku Solver")
    font = pygame.font.Font(None, 36)
    button_font = pygame.font.Font(None, 30)

    sudoku_grid = generate_random_sudoku()
    solved_grid = [row[:] for row in sudoku_grid]
    solve_sudoku_with_graph(solved_grid)
    print("Original Sudoku:")
    print_sudoku(sudoku_grid)

    solve_button = pygame.Rect(175, 520, 200, 50)
    hint_button = pygame.Rect(400, 520, 150, 50)
    graph_info = []

    running = True
    selected_cell = None

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if solve_button.collidepoint(event.pos):
                    sudoku_grid = [row[:] for row in solved_grid]
                elif hint_button.collidepoint(event.pos):
                    hint = get_hint(sudoku_grid, solved_grid)
                    if hint:
                        i, j, value = hint
                        sudoku_grid[i][j] = value
                        graph_info.append(f"Hint: Cell ({i+1},{j+1}) = {value}")
                else:
                    x, y = event.pos
                    if 50 < x < 500 and 50 < y < 500:
                        row = (y - 50) // 50
                        col = (x - 50) // 50
                        selected_cell = (row, col)
            elif event.type == pygame.KEYDOWN and selected_cell:
                row, col = selected_cell
                if event.key == pygame.K_0:
                    sudoku_grid[row][col] = 0
                elif pygame.K_1 <= event.key <= pygame.K_9:
                    sudoku_grid[row][col] = event.key - pygame.K_0
                graph_info.append(f"User updated Cell ({row+1},{col+1}) = {sudoku_grid[row][col]}")

        draw_grid(screen, sudoku_grid, font)
        pygame.draw.rect(screen, (100, 200, 100), solve_button)
        pygame.draw.rect(screen, (100, 100, 200), hint_button)
        solve_text = button_font.render("Solve Sudoku", True, (255, 255, 255))
        hint_text = button_font.render("Hint", True, (255, 255, 255))
        screen.blit(solve_text, (solve_button.x + 20, solve_button.y + 10))
        screen.blit(hint_text, (hint_button.x + 40, hint_button.y + 10))

        draw_graph_update(graph_info[-10:], font, screen)
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
