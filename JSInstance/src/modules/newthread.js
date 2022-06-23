const utils = require("../utils");
const threads = require("../data/threads");
const {getOrFetchChannel} = require("../utils");

module.exports = ({ bot, knex, config, commands }) => {
  commands.addInboxServerCommand("newthread", "<userId:userId>", async (msg, args, thread) => {
    const user = bot.users.get(args.userId) || await bot.getRESTUser(args.userId).catch(() => null);
    if (! user) {
      utils.postSystemMessageWithFallback(msg.channel, thread, "Benutzer nicht gefunden");
      return;
    }

    if (user.bot) {
      utils.postSystemMessageWithFallback(msg.channel, thread, "Du klannst keinen Thread mit einem Bot erstellen");
      return;
    }

    const existingThread = await threads.findOpenThreadByUserId(user.id);
    if (existingThread) {
      utils.postSystemMessageWithFallback(msg.channel, thread, `Thread kann nicht erstellt werden. Benutzer hat bereits einen offenen Thread: <#${existingThread.channel_id}>`);
      return;
    }

    const createdThread = await threads.createNewThreadForUser(user, {
      quiet: true,
      ignoreRequirements: true,
      ignoreHooks: true,
      source: "command",
    });

    createdThread.postSystemMessage(`Thread wurde geöffnet von ${msg.author.username}#${msg.author.discriminator}`);

    const channel = await getOrFetchChannel(bot, msg.channel.id);
    channel.createMessage(`Thread geöffnet: <#${createdThread.channel_id}>`);
  });
};
