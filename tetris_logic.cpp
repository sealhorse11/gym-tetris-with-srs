#include "tetris_logic.hpp"
#include <vector>
#include <random>
#include <algorithm>
#include <chrono>
#include <iostream>

std::vector<Point> Piece::get_blocks()
{
    std::vector<Point> blocks;
    for (int i = 0; i < 4; i++)
    {
        blocks.push_back(Point(pos.row + TETROMINOS[piece][rotation][i].row, pos.col + TETROMINOS[piece][rotation][i].col));
    }
    return blocks;
}

bool Piece::safe()
{
    std::vector<Point> blocks = get_blocks();
    for (int i = 0; i < 4; i++)
    {
        if (!blocks[i].safe())
        {
            return false;
        }
    }
    return true;
}

Game::Game()
{
    score = 0;
    combo = 0;
    level = 1;

    game_over = false;

    opponent = NULL; // set opponent in main.cpp

    back_to_back = false;
    t_spin = false;
    mini_t_spin = false;

    recently_held = false;
    hold_piece = -1;

    current_piece = NULL;

    init_board();
    get_next_piece();
}

void Game::init_board()
{
    for (int i = 0; i < BOARD_HEIGHT; i++)
        for (int j = 0; j < BOARD_WIDTH; j++)
            board[i][j] = -1;
}

void Game::make_bag()
{
    std::vector<int> bag;
    for (int i = 0; i < 7; i++)
        bag.push_back(i);

    std::shuffle(bag.begin(), bag.end(), std::default_random_engine(std::chrono::system_clock::now().time_since_epoch().count()));

    for (int i = 0; i < 7; i++)
        next_pieces.push_back(bag[i]);
}

int Game::get_next_piece()
{
    if(game_over)
        return -1;

    recently_held = false;
    if (next_pieces.size() < 7)
        make_bag();
    if(current_piece != NULL){
        delete current_piece;
    }
    current_piece = new Piece(next_pieces[0], 0, get_spawn_point(next_pieces[0]));
    next_pieces.erase(next_pieces.begin());

    if(current_piece->pos.row == -1){
        game_over = true;
        lock();
        return -1;
    }
    return 0;
}

Point Game::get_spawn_point(int piece)
{
    Piece spawn_piece = Piece(piece, 0, Point(20, 4));
    if(is_piece_safe(spawn_piece)){
        return spawn_piece.pos;
    }

    spawn_piece.pos.row--;
    if(is_piece_safe(spawn_piece)){
        return spawn_piece.pos;
    }

    return Point(-1, -1);   // Game Over
}

Point Game::get_shadow_point()
{
    Piece shadow_piece = Piece(current_piece->piece, current_piece->rotation, current_piece->pos);
    while(true)
    {
        shadow_piece.pos.row++;
        if(!is_piece_safe(shadow_piece))
        {
            shadow_piece.pos.row--;
            break;
        }
    }
    return shadow_piece.pos;
}

void Game::move_left()
{
    Piece new_piece = Piece(current_piece->piece, current_piece->rotation, current_piece->pos);
    new_piece.pos.col--;
    if(is_piece_safe(new_piece)){
        current_piece->pos.col--;
        t_spin = false;
        mini_t_spin = false;
    }
}

void Game::move_right()
{
    Piece new_piece = Piece(current_piece->piece, current_piece->rotation, current_piece->pos);
    new_piece.pos.col++;
    if(is_piece_safe(new_piece)){
        current_piece->pos.col++;
        t_spin = false;
        mini_t_spin = false;
    }
}

void Game::soft_drop()
{
    Piece new_piece = Piece(current_piece->piece, current_piece->rotation, current_piece->pos);
    new_piece.pos.row++;
    if(is_piece_safe(new_piece)){
        current_piece->pos.row++;
        t_spin = false;
        mini_t_spin = false;
    }
}

void Game::hard_drop()
{
    Point shadow_point = get_shadow_point();
    current_piece->pos.row = shadow_point.row;
    lock();
}

void Game::rotate_counterclockwise()
{
    if(current_piece->piece == 3)
        return;
    
    Piece new_piece;
    Point kick_pos;
    int tmp;

    for(int test = 0; test < 5; test++)
    {
        if(current_piece->piece == 0)
            if(current_piece->rotation == 2 && test == 3 || current_piece->rotation == 0 && test == 4)
                continue;
        
        if(current_piece->piece == 4)
            kick_pos = WALL_KICK_I_COUNTERCLOCKWISE[current_piece->rotation][test];
        else
            kick_pos = WALL_KICK_OTHER_COUNTERCLOCKWISE[current_piece->rotation][test];
        
        tmp = kick_pos.row;
        kick_pos.row = -kick_pos.col;
        kick_pos.col = tmp;

        new_piece = Piece(current_piece->piece, (current_piece->rotation + 3) % 4, current_piece->pos + kick_pos);
        if(is_piece_safe(new_piece)){
            current_piece->rotation = (current_piece->rotation + 3) % 4;
            current_piece->pos = new_piece.pos;

            if(current_piece->piece == 0 && is_on_ground())
            {
                Point corner[4] = {
                    Point(-1, -1), Point(1, -1), Point(1, 1), Point(-1, 1)
                };
                Point curr_corner;
                int blocked = 0;
                for(int i = 0; i < 4; i++)
                {
                    curr_corner = current_piece->pos + corner[i];
                    if(!curr_corner.safe() || board[curr_corner.row][curr_corner.col] != -1)
                    {
                        blocked++;
                    }
                }

                if(blocked >= 3)
                    t_spin = true;
                else if(blocked >= 2)
                    mini_t_spin = true;
            }
            return;
        }
    }
}

void Game::rotate_clockwise()
{
    if(current_piece->piece == 3)
        return;
    
    Piece new_piece;
    Point kick_pos;
    int tmp;

    for(int test = 0; test < 5; test++)
    {
        if(current_piece->piece == 0)
            if(current_piece->rotation == 0 && test == 3 || current_piece->rotation == 2 && test == 2)
                continue;
        
        if(current_piece->piece == 4)
            kick_pos = WALL_KICK_I_CLOCKWISE[current_piece->rotation][test];
        else
            kick_pos = WALL_KICK_OTHER_CLOCKWISE[current_piece->rotation][test];
        
        tmp = kick_pos.row;
        kick_pos.row = -kick_pos.col;
        kick_pos.col = tmp;

        new_piece = Piece(current_piece->piece, (current_piece->rotation + 1) % 4, current_piece->pos + kick_pos);
        if(is_piece_safe(new_piece)){
            current_piece->rotation = (current_piece->rotation + 1) % 4;
            current_piece->pos = new_piece.pos;

            if(current_piece->piece == 0 && is_on_ground())
            {
                Point corner[4] = {
                    Point(-1, -1), Point(1, -1), Point(1, 1), Point(-1, 1)
                };
                Point curr_corner;
                int blocked = 0;
                for(int i = 0; i < 4; i++)
                {
                    curr_corner = current_piece->pos + corner[i];
                    if(!curr_corner.safe() || board[curr_corner.row][curr_corner.col] != -1)
                    {
                        blocked++;
                    }
                }

                if(blocked >= 3)
                    t_spin = true;
                else if(blocked >= 2)
                    mini_t_spin = true;
            }
            return;
        }
    }
}

void Game::hold()
{
    if(!recently_held){
        if(hold_piece == -1){
            hold_piece = current_piece->piece;
            get_next_piece();
        }
        else{
            int temp = current_piece->piece;
            current_piece->piece = hold_piece;
            hold_piece = temp;
            current_piece->pos = get_spawn_point(current_piece->piece);
        }
        recently_held = true;
    }
}

void Game::lock()
{
    std::vector<Point> blocks = current_piece->get_blocks();
    for (int i = 0; i < 4; i++)
    {
        board[blocks[i].row][blocks[i].col] = current_piece->piece;
    }
    line_clear();
    if(current_piece->pos.row < VISIBLE_HEIGHT)
    {
        game_over = true;
    }
    get_next_piece();
}

void Game::line_clear()
{
    // update the board with line clear
    std::vector<int> target_lines;
    for(int i = BOARD_HEIGHT - VISIBLE_HEIGHT - 1; i < BOARD_HEIGHT; i++)
    {
        for(int j = 0; j < BOARD_WIDTH; j++)
        {
            if(board[i][j] == -1)
            {
                break;
            }
            if(j == BOARD_WIDTH - 1)
            {
                target_lines.push_back(i);
            }
        }
    }
    // add here to set delay for line clear animation
    for(int target_line: target_lines)
    {
        for(int i = target_line; i > 0; i--)
        {
            for(int j = 0; j < BOARD_WIDTH; j++)
            {
                board[i][j] = board[i - 1][j];
            }
        }
    }

    if(target_lines.empty())
    {
        if(opponent != NULL)
            create_garbage();
        combo = 0;
        t_spin = false;
        mini_t_spin = false;
        return;
    }

    // judge attack with cleared lines
    if(opponent != NULL)
    {
        std::vector<int> attack_lines = attack(target_lines.size());

        while(!gauges.empty() && !attack_lines.empty())
        {
            int next_gauge = gauges.front();
            gauges.erase(gauges.begin());

            int next_attack = attack_lines.front();
            attack_lines.erase(attack_lines.begin());

            if(next_gauge > next_attack)
            {
                gauges.insert(gauges.begin(), next_gauge - next_attack);
            }
            else if(next_gauge < next_attack)
            {
                attack_lines.insert(attack_lines.begin(), next_attack - next_gauge);
            }
        }

        if(gauges.empty())
        {
            opponent->gauges.insert(opponent->gauges.begin(), attack_lines.begin(), attack_lines.end());
        }
        else if(attack_lines.empty())
        {
            create_garbage();
        }
    }

    combo++;
    t_spin = false;
    mini_t_spin = false;
}

std::vector<int> Game::attack(int lines)
{
    std::default_random_engine gen(std::chrono::system_clock::now().time_since_epoch().count());
    std::uniform_int_distribution<int> dis(0, 9);
    
    if(current_piece->piece != 0)
    {
        t_spin = false;
        mini_t_spin = false;
    }
    std::vector<int> attack_lines;
    
    bool all_cleared = true;
    for(int i = 0; i < BOARD_HEIGHT; i++)
    {
        for(int j = 0; j < BOARD_WIDTH; j++)
        {
            if(board[i][j] != -1)
            {
                all_cleared = false;
                break;
            }
        }
        if(!all_cleared)
            break;
    }

    if(all_cleared)
    {
        int remain = 10, tmp;
        while(remain > 0)
        {
            tmp = dis(gen) % 6 + 1;
            if(tmp > remain)
                tmp = remain;
            attack_lines.push_back(tmp);
            remain -= tmp;
        }
        return attack_lines;
    }


    if(lines == 1)
    {
        if(t_spin)
        {
            attack_lines.push_back(2);
            if(back_to_back)
            {
                attack_lines.push_back(1);
            }
            else
            {
                back_to_back = true;
            }
        }
        else if(mini_t_spin)
        {
            if(back_to_back)
            {
                attack_lines.push_back(1);
            }
            else
            {
                back_to_back = true;
            }
        }
        else
        {
            back_to_back = false;
        }
        
        if(combo > 1)
        {
            attack_lines.push_back(COMBO_DAMAGE[combo]);
        }
    }
    else if(lines == 2)
    {
        if(t_spin)
        {
            attack_lines.push_back(4);
            if(back_to_back)
            {
                attack_lines.push_back(1);
            }
            else
            {
                back_to_back = true;
            }
        }
        else if(mini_t_spin)
        {
            if(back_to_back)
            {
                attack_lines.push_back(1);
            }
            else
            {
                back_to_back = true;
            }
        }
        else
        {
            attack_lines.push_back(1);
            back_to_back = false;
        }
        
        if(combo > 1)
        {
            attack_lines.push_back(COMBO_DAMAGE[combo]);
        }
    }
    else if(lines == 3)
    {
        if(t_spin)
        {
            attack_lines.push_back(6);
            if(back_to_back)
            {
                attack_lines.push_back(1);
            }
            else
            {
                back_to_back = true;
            }
        }
        else
        {
            attack_lines.push_back(2);
            back_to_back = false;
        }
        
        if(combo > 1)
        {
            attack_lines.push_back(COMBO_DAMAGE[combo]);
        }
    }
    else if(lines == 4) // Tetris
    {
        attack_lines.push_back(4);
        if(back_to_back)
        {
            attack_lines.push_back(1);
        }
        else
        {
            back_to_back = true;
        }
        if(combo > 1)
        {
            attack_lines.push_back(COMBO_DAMAGE[combo]);
        }
    }
    return attack_lines;
}

void Game::create_garbage()
{
    std::default_random_engine gen(std::chrono::system_clock::now().time_since_epoch().count());
    std::uniform_int_distribution<int> dis(0, 9);

    if(gauges.empty())
        return;

    int total_lines = 0;
    for(int line: gauges)
    {
        total_lines += line;
    }

    for(int i = total_lines; i < BOARD_HEIGHT; i++)
    {
        for(int j = 0; j < BOARD_WIDTH; j++)
        {
            board[i - total_lines][j] = board[i][j];
        }
    }

    int start_line = BOARD_HEIGHT - total_lines;
    for(int line: gauges)
    {
        int blank = dis(gen);

        for(int i = 0; i < line; i++)
        {
            for(int j = 0; j < BOARD_WIDTH; j++)
            {
                if(j == blank)
                    board[start_line + i][j] = -1;   // blank
                else
                    board[start_line + i][j] = 7;    // garbage
            }
        }
        start_line += line;
    }

    gauges.clear();
}

bool Game::is_piece_safe(Piece _piece)
{
    std::vector<Point> blocks = _piece.get_blocks();
    for (int i = 0; i < 4; i++)
    {
        if (!blocks[i].safe() || board[blocks[i].row][blocks[i].col] != -1)
        {
            return false;
        }
    }
    return true;
}

bool Game::is_on_ground()
{
    return current_piece->pos.row == get_shadow_point().row;
}

int Game::get_held_piece()
{
    return hold_piece;
}

int* Game::get_next_pieces_top_five()
{
    for(int i = 0; i < 5; i++)
    {
        next_pieces_top_five[i] = next_pieces[i];
    }
    return next_pieces_top_five;
}

int Game::get_sum_of_gauge()
{
    int sum = 0;
    for(int line: gauges)
    {
        sum += line;
    }
    return sum;
}

int* Game::get_board()
{
    for(int i = VISIBLE_HEIGHT; i < BOARD_HEIGHT; i++)
    {
        for(int j = 0; j < BOARD_WIDTH; j++)
        {
            board_1d[(i - VISIBLE_HEIGHT) * BOARD_WIDTH + j] = board[i][j];
        }
    }

    Point shadow_pos = get_shadow_point();
    Piece shadow_piece = Piece(current_piece->piece, current_piece->rotation, shadow_pos);
    
    for(int i = 0; i < 4; i++)
    {
        Point block = shadow_piece.get_blocks()[i];
        if(block.row >= VISIBLE_HEIGHT)
        {
            board_1d[(block.row - VISIBLE_HEIGHT) * BOARD_WIDTH + block.col] = 8;
        }
    }

    for(int i = 0; i < 4; i++)
    {
        Point block = current_piece->get_blocks()[i];
        if(block.row >= VISIBLE_HEIGHT)
        {
            board_1d[(block.row - VISIBLE_HEIGHT) * BOARD_WIDTH + block.col] = current_piece->piece;
        }
    }

    return board_1d;
}

extern "C"
{
    Game* Game_new(){return new Game();}
    void Game_set_opponent(Game* self, Game* _opponent){self->set_opponent(_opponent);}
    bool Game_is_game_over(Game* self){return self->is_game_over();}

    void Game_move_left(Game* self){self->move_left();}
    void Game_move_right(Game* self){self->move_right();}
    void Game_soft_drop(Game* self){self->soft_drop();}
    void Game_hard_drop(Game* self){self->hard_drop();}
    void Game_rotate_counterclockwise(Game* self){self->rotate_counterclockwise();}
    void Game_rotate_clockwise(Game* self){self->rotate_clockwise();}

    void Game_hold(Game* self){self->hold();}
    void Game_lock(Game* self){self->lock();}

    bool Game_is_on_ground(Game* self){return self->is_on_ground();}

    int Game_get_held_piece(Game* self){return self->get_held_piece();}
    int* Game_get_next_pieces_top_five(Game* self){return self->get_next_pieces_top_five();}
    int Game_get_sum_of_gauge(Game* self){return self->get_sum_of_gauge();}
    int* Game_get_board(Game* self){return self->get_board();}

    void Game_delete(Game* self){delete self;}
}