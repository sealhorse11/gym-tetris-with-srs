#include <vector>

const int BOARD_WIDTH = 10;
const int BOARD_HEIGHT = 40;
const int VISIBLE_HEIGHT = 20;

const int COMBO_DAMAGE[] = {
    0, 0, 1, 1, 2, 2, 3, 3, 4, 4, 4, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5
};

const int NUMBER_OF_NEXT_PIECES = 5;

char ATTACK_TYPES[][22] = {
    "SINGLE", "DOUBLE", "TRIPLE", "TETRIS", "T-SPIN mini SINGLE", "T-SPIN mini DOUBLE", "T-SPIN SINGLE", "T-SPIN DOUBLE", "T-SPIN TRIPLE", "PERFECT CLEAR", "PERFECT CLEAR TETRIS", ""
};

struct Point{
    int row;
    int col;

    Point(): row(0), col(0){};
    Point(int _row, int _col): row(_row), col(_col){};
    void operator+=(Point &p){
        this->row += p.row;
        this->col += p.col;
    }
    Point operator+(Point &p){
        return Point(this->row + p.row, this->col + p.col);
    }
    Point operator - (){
        return Point(-this->row, -this->col);
    }
    bool safe(){
        return this->row >= 0 && this->row < BOARD_HEIGHT && this->col >= 0 && this->col < BOARD_WIDTH;
    }
};

const Point TETROMINOS[7][4][4] = {
    {   // T
        {Point(0, -1), Point(0, 0), Point(-1, 0), Point(0, 1)},
        {Point(1, 0), Point(0, 0), Point(-1, 0), Point(0, 1)},
        {Point(0, -1), Point(0, 0), Point(1, 0), Point(0, 1)},
        {Point(0, -1), Point(1, 0), Point(0, 0), Point(-1, 0)}
    },
    {   // S
        {Point(0, -1), Point(0, 0), Point(-1, 0), Point(-1, 1)},
        {Point(-1, 0), Point(0, 0), Point(1, 1), Point(0, 1)},
        {Point(1, -1), Point(1, 0), Point(0, 0), Point(0, 1)},
        {Point(-1, -1), Point(0, -1), Point(1, 0), Point(0, 0)}
    },
    {   // Z
        {Point(-1, -1), Point(-1, 0), Point(0, 0), Point(0, 1)},
        {Point(1, 0), Point(0, 0), Point(0, 1), Point(-1, 1)},
        {Point(0, -1), Point(0, 0), Point(1, 0), Point(1, 1)},
        {Point(1, -1), Point(0, -1), Point(0, 0), Point(-1, 0)}
    },
    {   // O
        {Point(0, 0), Point(-1, 0), Point(-1, 1), Point(0, 1)},
        {Point(0, 0), Point(-1, 0), Point(-1, 1), Point(0, 1)},
        {Point(0, 0), Point(-1, 0), Point(-1, 1), Point(0, 1)},
        {Point(0, 0), Point(-1, 0), Point(-1, 1), Point(0, 1)}
    },
    {   // I
        {Point(0, -1), Point(0, 0), Point(0, 1), Point(0, 2)},
        {Point(-1, 0), Point(0, 0), Point(1, 0), Point(2, 0)},
        {Point(0, -2), Point(0, -1), Point(0, 0), Point(0, 1)},
        {Point(-2, 0), Point(-1, 0), Point(0, 0), Point(1, 0)}
    },
    {   // J
        {Point(-1, -1), Point(0, -1), Point(0, 0), Point(0, 1)},
        {Point(1, 0), Point(0, 0), Point(-1, 0), Point(-1, 1)},
        {Point(0, -1), Point(0, 0), Point(1, 1), Point(0, 1)},
        {Point(1, -1), Point(1, 0), Point(0, 0), Point(-1, 0)}
    },
    {   // L
        {Point(0, -1), Point(0, 0), Point(0, 1), Point(-1, 1)},
        {Point(1, 0), Point(0, 0), Point(-1, 0), Point(1, 1)},
        {Point(1, -1), Point(0, -1), Point(0, 0), Point(0, 1)},
        {Point(-1, -1), Point(-1, 0), Point(0, 0), Point(1, 0)}
    }
};

const Point WALL_KICK_I_CLOCKWISE[4][5] = {
    {Point(1, 0), Point(-1, 0), Point(2, 0), Point(-1, -1), Point(2, 2)},
    {Point(0, -1), Point(-1, -1), Point(2, -1), Point(-1, 1), Point(2, -2)},
    {Point(-1, 0), Point(1, 0), Point(-2, 0), Point(1, 1), Point(-2, -1)},
    {Point(0, 1), Point(-2, 1), Point(1, 1), Point(-2, 2), Point(1, -1)}
};

const Point WALL_KICK_I_COUNTERCLOCKWISE[4][5] = {
    {Point(0, -1), Point(2, -1), Point(-1, -1), Point(2, -2), Point(-1, 1)},
    {Point(-1, 0), Point(1, 0), Point(-2, 0), Point(1, 1), Point(-2, -2)},
    {Point(0, 1), Point(1, 1), Point(-2, 1), Point(1, -1), Point(-2, 2)},
    {Point(1, 0), Point(-1, 0), Point(2, 0), Point(-1, -1), Point(2, 1)}
};

const Point WALL_KICK_OTHER_CLOCKWISE[4][5] = {
    {Point(0, 0), Point(-1, 0), Point(-1, 1), Point(0, -2), Point(-1, -2)},
    {Point(0, 0), Point(1, 0), Point(1, -1), Point(0, 2), Point(1, 2)},
    {Point(0, 0), Point(1, 0), Point(1, 1), Point(0, -2), Point(1, -2)},
    {Point(0, 0), Point(-1, 0), Point(-1, -1), Point(0, 2), Point(-1, 2)}
};

const Point WALL_KICK_OTHER_COUNTERCLOCKWISE[4][5] = {
    {Point(0, 0), Point(1, 0), Point(1, 1), Point(0, -2), Point(1, -2)},
    {Point(0, 0), Point(1, 0), Point(1, -1), Point(0, 2), Point(1, 2)},
    {Point(0, 0), Point(-1, 0), Point(-1, 1), Point(0, -2), Point(-1, -2)},
    {Point(0, 0), Point(-1, 0), Point(-1, -1), Point(0, 2), Point(-1, 2)}
};

struct Piece{
    int piece;
    int rotation;
    Point pos;
    
    Piece(): piece(0), rotation(0), pos(Point(0, 0)){};
    Piece(int _piece, int _rotation, Point _pos): piece(_piece), rotation(_rotation), pos(_pos){};
    std::vector<Point> get_blocks();
    bool safe();
};

struct Attack{
    char* type;
    int lines;
    int combo;
    bool back_to_back;

    Attack(): type(ATTACK_TYPES[11]), lines(0), combo(0), back_to_back(0){};
    Attack(char* _type, int _lines, int _combo, bool _back_to_back): type(_type), lines(_lines), combo(_combo), back_to_back(_back_to_back){};
};

class Game{
    public:
        Game();
        void set_opponent(Game *_opponent) {opponent = _opponent;};
        // Game* get_self() {return this;};
        bool is_game_over() {return game_over;};
        
        void move_left();
        void move_right();
        void soft_drop();
        void hard_drop();
        void rotate_counterclockwise();
        void rotate_clockwise();

        void hold();
        void lock();

        bool is_on_ground();

        int get_held_piece();
        int* get_next_pieces_top_five();
        int get_sum_of_gauge();
        int* get_board();

        Attack* get_last_attack();
        int get_sent_attack();

    private:
        Game *opponent;
        int next_pieces_top_five[5];
        int board_1d[VISIBLE_HEIGHT * BOARD_WIDTH];

        int board[BOARD_HEIGHT][BOARD_WIDTH];
        int score;
        int combo;
        int level;
        bool game_over;
        
        Piece *current_piece;

        bool back_to_back;
        bool t_spin;
        bool mini_t_spin;
        Attack last_attack;
        int sent_attack;

        bool recently_held;
        int hold_piece;
        std::vector<int> next_pieces;
        std::vector<int> gauges;

        void init_board();
        
        Point get_spawn_point(int piece);
        Point get_shadow_point();
        int get_next_piece();
        void make_bag();

        void line_clear();
        std::vector<int> attack(int lines);
        void create_garbage();

        bool is_piece_safe(Piece _piece);

};