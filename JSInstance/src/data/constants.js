module.exports = {
  THREAD_STATUS: {
    OPEN: 1,
    CLOSED: 2,
    SUSPENDED: 3
  },

  THREAD_MESSAGE_TYPE: {
    SYSTEM: 1,
    CHAT: 2,
    FROM_USER: 3,
    TO_USER: 4,
    LEGACY: 5,
    COMMAND: 6,
    SYSTEM_TO_USER: 7,
    REPLY_EDITED: 8,
    REPLY_DELETED: 9,
  },

  // https://discord.com/developers/docs/resources/channel#channel-object-channel-types
  DISOCRD_CHANNEL_TYPES: {
    GUILD_TEXT: 0,
    DM: 1,
    GUILD_VOICE: 2,
    GROUP_DM: 3,
    GUILD_CATEGORY: 4,
    GUILD_NEWS: 5,
    GUILD_STORE: 6,
  },

  // https://discord.com/developers/docs/resources/channel#message-object-message-activity-types
  DISCORD_MESSAGE_ACTIVITY_TYPES: {
    JOIN: 1,
    SPECTATE: 2,
    LISTEN: 3,
    JOIN_REQUEST: 5,
  },

  ACCIDENTAL_THREAD_MESSAGES: [
    "ok",
    "oki",
    "danke",
    "thx",
    "k",
    "kk",
    "dankee",
    "oke",
    "dangge",
    "dange",
    "uwu",
    "ok danke",
    "ok dange",
    "okii dankee",
    "oki dankee",
    "ok dangge",
    "ok thx",
    "ok kein problem",
  ],
};
