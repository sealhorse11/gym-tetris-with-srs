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
    combo = 0;
    das = 100;
    arr = 10;
    sdf = 2;
    lock_delay = 500;
    drop_delay = 1000;

    game_start_time = pygame_clock;
    first_on_ground = last_on_ground = 0;
    left_pressed_time = right_pressed_time = last_shifted = last_soft_dropped = 0;

    game_over = false;

    opponent = NULL; // set opponent in main.cpp

    back_to_back = false;
    t_spin = false;
    mini_t_spin = false;

    recently_held = false;
    held_piece = -1;

    current_piece = NULL;
    last_attack = Attack();
    sent_attack = 0;

    board_for_render = new int[VISIBLE_HEIGHT * BOARD_WIDTH];

    // 10 channels for observation
    // board, current piece, held piece, next 5 pieces, btb, combo
    obs = new int[10 * VISIBLE_HEIGHT * BOARD_WIDTH];

    init_board();
    get_next_piece();
}

Game::Game(int _das, int _arr, int _sdf, int _time, int _lock_delay=500, int _drop_delay=1000)
:das(_das), arr(_arr), sdf(_sdf), lock_delay(_lock_delay), drop_delay(_drop_delay)
{
    combo = 0;

    pygame_clock = _time;
    game_start_time = pygame_clock;
    first_on_ground = last_on_ground = 0;
    left_pressed_time = right_pressed_time = last_shifted = last_soft_dropped = 0;
    last_dropped = pygame_clock;

    game_over = false;

    opponent = NULL; // set opponent in main.cpp

    back_to_back = false;
    t_spin = false;
    mini_t_spin = false;

    recently_held = false;
    held_piece = -1;

    current_piece = NULL;
    last_attack = Attack();
    sent_attack = 0;

    board_for_render = new int[VISIBLE_HEIGHT * BOARD_WIDTH];

    // 10 channels for observation
    // board, current piece, held piece, next 5 pieces, btb, combo
    obs = new int[10 * VISIBLE_HEIGHT * BOARD_WIDTH];

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
    if(current_piece != NULL)
        delete current_piece;

    current_piece = new Piece(next_pieces[0], 0, get_spawn_point(next_pieces[0]));
    next_pieces.erase(next_pieces.begin());

    if(current_piece->pos.row == -1)
    {
        game_over = true;
        lock(true);
        return -1;
    }
    last_dropped = pygame_clock;
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

    game_over = true;
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

bool Game::move_left()
{
    Piece new_piece = Piece(current_piece->piece, current_piece->rotation, current_piece->pos);
    new_piece.pos.col--;
    if(is_piece_safe(new_piece))
    {
        if(left_pressed_time == 0)
            left_pressed_time = pygame_clock;
        else if(left_pressed_time < right_pressed_time)
            return false;
        else if(pygame_clock - left_pressed_time >= das && (last_shifted == 0 || pygame_clock - last_shifted >= arr))
            last_shifted = pygame_clock;
        else
            return false;
        
        current_piece->pos.col--;
        t_spin = false;
        mini_t_spin = false;
        return true;
    }
    return false;
}

bool Game::move_right()
{
    Piece new_piece = Piece(current_piece->piece, current_piece->rotation, current_piece->pos);
    new_piece.pos.col++;
    if(is_piece_safe(new_piece))
    {
        if(right_pressed_time == 0)
            right_pressed_time = pygame_clock;
        else if(right_pressed_time < left_pressed_time)
            return false;
        else if(pygame_clock - right_pressed_time >= das && (last_shifted == 0 || pygame_clock - last_shifted >= arr))
            last_shifted = pygame_clock;
        else
            return false;
        
        current_piece->pos.col++;
        t_spin = false;
        mini_t_spin = false;
        return true;
    }
    return false;
}

bool Game::soft_drop(bool by_gravity = false)
{
    Piece new_piece = Piece(current_piece->piece, current_piece->rotation, current_piece->pos);
    new_piece.pos.row++;
    if(is_piece_safe(new_piece))
    {
        if(by_gravity)
            last_dropped = pygame_clock;
        else if(last_soft_dropped == 0 || pygame_clock - last_soft_dropped >= sdf)
            last_soft_dropped = pygame_clock;
        else
            return false;
        
        current_piece->pos.row++;
        t_spin = false;
        mini_t_spin = false;
        return true;
    }
    return false;
}

void Game::off_left()
{
    left_pressed_time = 0;
    last_shifted = 0;
}

void Game::off_right()
{
    right_pressed_time = 0;
    last_shifted = 0;
}

void Game::off_soft_drop()
{
    last_soft_dropped = 0;
}

void Game::hard_drop()
{
    Point shadow_point = get_shadow_point();
    current_piece->pos.row = shadow_point.row;
    lock(true);
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

bool Game::hold()
{
    if(!recently_held)
    {
        if(held_piece == -1)
        {
            held_piece = current_piece->piece;
            get_next_piece();
        }
        else
        {
            int temp = current_piece->piece;
            current_piece->piece = held_piece;
            held_piece = temp;
            current_piece->pos = get_spawn_point(current_piece->piece);
        }
        recently_held = true;
        last_dropped = pygame_clock;
        return true;
    }
    return false;
}

bool Game::lock(bool force_lock = false)
{
    if(!force_lock)
    {
        if(!is_on_ground())
        {
            if(pygame_clock - last_dropped >= drop_delay){
                soft_drop(true);
                last_dropped = pygame_clock;
                std::cout << pygame_clock << std::endl;
            }
            return false;
        }
        else if(first_on_ground == 0)
        {
            first_on_ground = pygame_clock;
            last_on_ground = first_on_ground;
        }
        else
            last_on_ground = pygame_clock;

        if(pygame_clock - first_on_ground < lock_delay * 5 && pygame_clock - last_on_ground < lock_delay)
            return false;
    }


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
    piece_count++;
    first_on_ground = 0;
    last_on_ground = 0;

    return true;
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


    // judge attack with cleared lines
    if(target_lines.empty())
    {
        if(opponent != NULL)
            create_garbage();
        combo = 0;
        t_spin = false;
        mini_t_spin = false;
        last_attack = Attack();
        return;
    }

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

    if(gauges.empty() && opponent != NULL)
    {
        opponent->gauges.insert(opponent->gauges.begin(), attack_lines.begin(), attack_lines.end());
    }
    else if(attack_lines.empty())
    {
        create_garbage();
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
        if(lines==4)
        {
            attack_lines.push_back(4);
            if (back_to_back)
            {
                attack_lines.push_back(1);
                last_attack = Attack(ATTACK_TYPES[10], 15, 0, 1);
            }
            else
            {
                last_attack = Attack(ATTACK_TYPES[10], 14, 0, 0);
                back_to_back = true;
            }
        }
        else
        {
            last_attack = Attack(ATTACK_TYPES[9], 10, 0, 0);
            back_to_back = false;
        }
        return attack_lines;
    }


    if(lines == 1)
    {
        if(t_spin)
        {
            last_attack = Attack(ATTACK_TYPES[6], 2, combo, back_to_back);
            attack_lines.push_back(2);
            if(back_to_back)
            {
                last_attack.lines++;
                attack_lines.push_back(1);
            }
            else
            {
                back_to_back = true;
            }
        }
        else if(mini_t_spin)
        {
            last_attack = Attack(ATTACK_TYPES[4], 0, combo, back_to_back);
            if(back_to_back)
            {
                last_attack.lines++;
                attack_lines.push_back(1);
            }
            else
            {
                back_to_back = true;
            }
        }
        else
        {
            last_attack = Attack(ATTACK_TYPES[0], 0, combo, false);
            back_to_back = false;
        }
        
        if(combo > 1)
        {
            last_attack.lines += COMBO_DAMAGE[combo];
            attack_lines.push_back(COMBO_DAMAGE[combo]);
        }
    }
    else if(lines == 2)
    {
        if(t_spin)
        {
            last_attack = Attack(ATTACK_TYPES[7], 4, combo, back_to_back);
            attack_lines.push_back(4);
            if(back_to_back)
            {
                last_attack.lines++;
                attack_lines.push_back(1);
            }
            else
            {
                back_to_back = true;
            }
        }
        else if(mini_t_spin)
        {
            last_attack = Attack(ATTACK_TYPES[5], 1, combo, back_to_back);
            if(back_to_back)
            {
                last_attack.lines++;
                attack_lines.push_back(1);
            }
            else
            {
                back_to_back = true;
            }
        }
        else
        {
            last_attack = Attack(ATTACK_TYPES[1], 1, combo, false);
            attack_lines.push_back(1);
            back_to_back = false;
        }
        
        if(combo > 1)
        {
            last_attack.lines += COMBO_DAMAGE[combo];
            attack_lines.push_back(COMBO_DAMAGE[combo]);
        }
    }
    else if(lines == 3)
    {
        if(t_spin)
        {
            last_attack = Attack(ATTACK_TYPES[8], 6, combo, back_to_back);
            attack_lines.push_back(6);
            if(back_to_back)
            {
                last_attack.lines++;
                attack_lines.push_back(1);
            }
            else
            {
                back_to_back = true;
            }
        }
        else
        {
            last_attack = Attack(ATTACK_TYPES[2], 2, combo, false);
            attack_lines.push_back(2);
            back_to_back = false;
        }
        
        if(combo > 1)
        {
            last_attack.lines += COMBO_DAMAGE[combo];
            attack_lines.push_back(COMBO_DAMAGE[combo]);
        }
    }
    else if(lines == 4) // Tetris
    {
        last_attack = Attack(ATTACK_TYPES[3], 4, combo, back_to_back);
        attack_lines.push_back(4);
        if(back_to_back)
        {
            last_attack.lines++;
            attack_lines.push_back(1);
        }
        else
        {
            back_to_back = true;
        }
        if(combo > 1)
        {
            last_attack.lines += COMBO_DAMAGE[combo];
            attack_lines.push_back(COMBO_DAMAGE[combo]);
        }
    }
    sent_attack += last_attack.lines;
    return attack_lines;
}

void Game::create_garbage()
{
    if(gauges.empty() || opponent == NULL)
        return;

    std::default_random_engine gen(std::chrono::system_clock::now().time_since_epoch().count());
    std::uniform_int_distribution<int> dis(0, 9);

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

bool Game::is_on_ground() {return current_piece->pos.row == get_shadow_point().row;}

int Game::get_held_piece(){return held_piece;};

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

int* Game::get_board_for_render()
{
    for(int i = 0; i < VISIBLE_HEIGHT; i++)
    {
        for(int j = 0; j < BOARD_WIDTH; j++)
        {
            board_for_render[i * BOARD_WIDTH + j] = board[i + VISIBLE_HEIGHT][j];
        }
    }

    Point shadow_pos = get_shadow_point();
    Piece shadow_piece = Piece(current_piece->piece, current_piece->rotation, shadow_pos);

    for (int i = 0; i < 4; i++)
    {
        Point block = shadow_piece.get_blocks()[i];
        if (block.row >= VISIBLE_HEIGHT)
        {
            board_for_render[(block.row - VISIBLE_HEIGHT) * BOARD_WIDTH + block.col] = 8;
        }
    }

    for (int i = 0; i < 4; i++)
    {
        Point block = current_piece->get_blocks()[i];
        if (block.row >= VISIBLE_HEIGHT)
        {
            board_for_render[(block.row - VISIBLE_HEIGHT) * BOARD_WIDTH + block.col] = current_piece->piece;
        }
    }

    return board_for_render;
}

int* Game::get_obs()
{
    // board
    const int CHANNEL_FACTOR = VISIBLE_HEIGHT * BOARD_WIDTH;
    for(int i = 0; i < VISIBLE_HEIGHT; i++)
        for(int j = 0; j < BOARD_WIDTH; j++)
            obs[i * BOARD_WIDTH + j] = board[i + VISIBLE_HEIGHT][j];

    // current piece
    Piece curr = Piece(current_piece->piece, 0, Point(22, 4));
    for(int i = 0; i < 4; i++)
    {
        Point block = current_piece->get_blocks()[i];
        obs[1 * CHANNEL_FACTOR + (block.row - VISIBLE_HEIGHT) * BOARD_WIDTH + block.col] = current_piece->piece;
    }

    // held piece
    if(held_piece != -1)
    {
        Piece held = Piece(held_piece, 0, Point(22, 4));
        for(int i = 0; i < 4; i++)
        {
            Point block = held.get_blocks()[i];
            obs[2 * CHANNEL_FACTOR + (block.row - VISIBLE_HEIGHT) * BOARD_WIDTH + block.col] = held_piece;
        }
    }

    // next 5 pieces
    for(int i = 0; i < 5; i++)
    {
        Piece next = Piece(next_pieces[i], 0, Point(22, 4));
        for(int j = 0; j < 4; j++)
        {
            Point block = next.get_blocks()[j];
            obs[(3 + i) * CHANNEL_FACTOR + (block.row - VISIBLE_HEIGHT) * BOARD_WIDTH + block.col] = next_pieces[i];
        }
    }

    // btb
    if(back_to_back)
        for(int i = 0; i < VISIBLE_HEIGHT; i++)
            for(int j = 0; j < BOARD_WIDTH; j++)
                obs[8 * CHANNEL_FACTOR + i * BOARD_WIDTH + j] = 1;
    
    // combo
    int row_for_combo = combo <= VISIBLE_HEIGHT ? combo : VISIBLE_HEIGHT - 1;
    for(int j = 0; j < BOARD_WIDTH; j++)
        obs[9 * CHANNEL_FACTOR + (VISIBLE_HEIGHT - 1 - row_for_combo) * BOARD_WIDTH + j] = 1;

    return obs;
}

Attack* Game::get_last_attack(){return &last_attack;};
int Game::get_sent_attack(){return sent_attack;};
int Game::get_piece_count(){return piece_count;};

int Game::get_field_height()
{
    for(int i = 0; i < BOARD_HEIGHT; i++)
    {
        for(int j = 0; j < BOARD_WIDTH; j++)
        {
            if(board[i][j] != -1)
            {
                return BOARD_HEIGHT - 1 - i;
            }
        }
    }
    return 0;
}

int Game::get_game_time(){return (int)(pygame_clock - game_start_time);};

extern "C"
{
    Game* Game_new(){return new Game();}
    Game* Game_new_in_detail(int _das, int _arr, int _sdf, int _lock_delay, int _drop_delay, int _time){return new Game(_das, _arr, _sdf, _time, _lock_delay, _drop_delay);}
    // void Game_set_opponent(Game* self, Game* _opponent){self->set_opponent(_opponent);}
    bool Game_is_game_over(Game* self){return self->is_game_over();}

    bool Game_move_left(Game* self){return self->move_left();}
    bool Game_move_right(Game* self){return self->move_right();}
    bool Game_soft_drop(Game* self){return self->soft_drop();}

    void Game_off_left(Game* self){self->off_left();}
    void Game_off_right(Game* self){self->off_right();}
    void Game_off_soft_drop(Game* self){self->off_soft_drop();}

    void Game_hard_drop(Game* self){self->hard_drop();}
    void Game_rotate_counterclockwise(Game* self){self->rotate_counterclockwise();}
    void Game_rotate_clockwise(Game* self){self->rotate_clockwise();}

    bool Game_hold(Game* self){return self->hold();}
    bool Game_lock(Game* self){return self->lock(false);}

    bool Game_is_on_ground(Game* self){return self->is_on_ground();}

    int Game_get_held_piece(Game* self){return self->get_held_piece();}
    int* Game_get_next_pieces_top_five(Game* self){return self->get_next_pieces_top_five();}
    int Game_get_sum_of_gauge(Game* self){return self->get_sum_of_gauge();}
    
    int* Game_get_board_for_render(Game* self){return self->get_board_for_render();}
    int* Game_get_obs(Game* self){return self->get_obs();}

    char* Game_get_last_attack_type(Game* self){return self->get_last_attack()->type;}
    int Game_get_last_attack_lines(Game* self){return self->get_last_attack()->lines;}
    int Game_get_last_attack_combo(Game* self){return self->get_last_attack()->combo;}
    bool Game_get_last_attack_back_to_back(Game* self){return self->get_last_attack()->back_to_back;}

    // for information at the observation
    int Game_get_sent_attack(Game* self){return self->get_sent_attack();}
    int Game_get_field_height(Game* self){return self->get_field_height();}
    int Game_get_piece_count(Game* self){return self->get_piece_count();}
    int Game_get_time(Game* self){return self->get_game_time();}
    void Game_set_time(Game* self, int _time){self->set_game_time(_time);}

    void Game_delete(Game* self){delete self;}
}