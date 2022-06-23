module.exports = ({ bot, knex, config, commands }) => {
  commands.addInboxThreadCommand("alert", "[opt:string]", async (msg, args, thread) => {
    if (args.opt && args.opt.startsWith("c")) {
      await thread.removeAlert(msg.author.id)
      await thread.postSystemMessage("Message-Alert abgebrochen");
    } else {
      await thread.addAlert(msg.author.id);
      await thread.postSystemMessage(`Pinge ${msg.author.username}#${msg.author.discriminator} wenn dieser Thread eine neue Antwort bekommt.`);
    }
  }, { allowSuspended: true });
};
