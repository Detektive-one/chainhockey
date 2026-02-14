# Network Protocol Documentation

## Message Types

### Client → Server Messages

#### `create_room`
Creates a new game room. Server responds with `room_created`.

```json
{
  "type": "create_room"
}
```

#### `join_room`
Joins an existing room by room ID. Server responds with `room_joined` or `error`.

```json
{
  "type": "join_room",
  "room_id": "ABC123"
}
```

#### `player_input`
Sends player input (mouse position, keyboard state) to server for forwarding to other player.

```json
{
  "type": "player_input",
  "input": {
    "mouse_x": 600,
    "mouse_y": 350,
    "keys": {
      "w": false,
      "a": false,
      "s": false,
      "d": false
    }
  }
}
```

#### `game_state`
Sends game state update (puck position, scores, etc.) to server for synchronization.

```json
{
  "type": "game_state",
  "state": {
    "puck": {"x": 600, "y": 350, "vel_x": 5, "vel_y": -3},
    "player1_score": 2,
    "player2_score": 1,
    "time_remaining": 240
  }
}
```

### Server → Client Messages

#### `room_created`
Sent when a room is successfully created.

```json
{
  "type": "room_created",
  "room_id": "ABC123",
  "player_num": 1
}
```

#### `room_joined`
Sent when successfully joining a room.

```json
{
  "type": "room_joined",
  "room_id": "ABC123",
  "player_num": 2
}
```

#### `player_connected`
Notifies when another player joins the room.

```json
{
  "type": "player_connected",
  "player_num": 2
}
```

#### `player_disconnected`
Notifies when a player leaves the room.

```json
{
  "type": "player_disconnected",
  "player_num": 2
}
```

#### `player_input`
Forwarded player input from other player.

```json
{
  "type": "player_input",
  "player_num": 1,
  "input": {
    "mouse_x": 600,
    "mouse_y": 350
  }
}
```

#### `game_state`
Forwarded game state from other player.

```json
{
  "type": "game_state",
  "state": {
    "puck": {"x": 600, "y": 350, "vel_x": 5, "vel_y": -3},
    "player1_score": 2,
    "player2_score": 1
  }
}
```

#### `error`
Error message from server.

```json
{
  "type": "error",
  "message": "Room not found"
}
```

## Game State Synchronization Strategy

### Authoritative Client Approach
- Player 1 is the host and authoritative for game state
- Player 1 sends game state updates to server
- Server forwards to Player 2
- Player 2 applies received state with interpolation/smoothing

### Input Synchronization
- Both players send input to server
- Server forwards input to other player
- Each player applies their own input immediately
- Remote input is applied with slight delay for network latency

## Room System

- Rooms are identified by 6-character alphanumeric codes
- Maximum 2 players per room
- Rooms are automatically cleaned up when empty
- Room creator is Player 1, joiner is Player 2

