const utils = require("../utils");
const {
  setModeratorDefaultRoleOverride,
  resetModeratorDefaultRoleOverride,

  setModeratorThreadRoleOverride,
  resetModeratorThreadRoleOverride,

  getModeratorThreadDisplayRoleName,
  getModeratorDefaultDisplayRoleName,
} = require("../data/displayRoles");
const {getOrFetchChannel} = require("../utils");

module.exports = ({ bot, knex, config, commands }) => {
  if (! config.allowChangingDisplayRole) {
    return;
  }

  function resolveRoleInput(input) {
    if (utils.isSnowflake(input)) {
      return utils.getInboxGuild().roles.get(input);
    }

    return utils.getInboxGuild().roles.find(r => r.name.toLowerCase() === input.toLowerCase());
  }

  // Get display role for a thread
  commands.addInboxThreadCommand("role", [], async (msg, args, thread) => {
    const displayRole = await getModeratorThreadDisplayRoleName(msg.member, thread.id);
    if (displayRole) {
      thread.postSystemMessage(`Deine angezeigte Rolle ist derzeit **${displayRole}**`);
    } else {
      thread.postSystemMessage("Deine Rolle wird bei Antworten in diesem Thread nicht angezeigt");
    }
  }, { allowSuspended: true });

  // Reset display role for a thread
  commands.addInboxThreadCommand("role reset", [], async (msg, args, thread) => {
    await resetModeratorThreadRoleOverride(msg.member.id, thread.id);

    const displayRole = await getModeratorThreadDisplayRoleName(msg.member, thread.id);
    if (displayRole) {
      thread.postSystemMessage(`Deine angezeigte Rolle wurde zurückgesetzt. Sie ist nun **${displayRole}**.`);
    } else {
      thread.postSystemMessage("Deine angezeigte Rolle wurde zurückgesetzt. Es wird nun keine angezeigt.");
    }
  }, {
    aliases: ["role_reset", "reset_role"],
    allowSuspended: true,
  });

  // Set display role for a thread
  commands.addInboxThreadCommand("role", "<role:string$>", async (msg, args, thread) => {
    const role = resolveRoleInput(args.role);
    if (! role || ! msg.member.roles.includes(role.id)) {
      thread.postSystemMessage("Keine passende Rolle gefunden. Du musst die Rolle haben damit sie angezeigt werden kann.");
      return;
    }

    await setModeratorThreadRoleOverride(msg.member.id, thread.id, role.id);
    thread.postSystemMessage(`Deine angezeigte Rolle ist in diesem Thread nun **${role.name}**. Du kannst sie zurücksetzen mit \`${config.prefix}role reset\`.`);
  }, { allowSuspended: true });

  // Get default display role
  commands.addInboxServerCommand("role", [], async (msg, args, thread) => {
    const channel = await getOrFetchChannel(bot, msg.channel.id);
    const displayRole = await getModeratorDefaultDisplayRoleName(msg.member);
    if (displayRole) {
      channel.createMessage(`Deine standardmäßig angezeigte Rolle ist **${displayRole}**`);
    } else {
      channel.createMessage("Du hast keine Rolle die standardmäßig angezeigt wird.");
    }
  });

  // Reset default display role
  commands.addInboxServerCommand("role reset", [], async (msg, args, thread) => {
    await resetModeratorDefaultRoleOverride(msg.member.id);

    const channel = await getOrFetchChannel(bot, msg.channel.id);
    const displayRole = await getModeratorDefaultDisplayRoleName(msg.member);
    if (displayRole) {
      channel.createMessage(`Deine standardmäßig angezeigte Rolle wurde zurückgesetzt. Deine Nachrichten haben nun die Rolle **${displayRole}**.`);
    } else {
      channel.createMessage("Deine standardmäßig angezeigte Rolle wurde zurückgesetzt. Deine Nachrichten haben nun keine Rolle.");
    }
  }, {
    aliases: ["role_reset", "reset_role"],
  });

  // Set default display role
  commands.addInboxServerCommand("role", "<role:string$>", async (msg, args, thread) => {
    const channel = await getOrFetchChannel(bot, msg.channel.id);
    const role = resolveRoleInput(args.role);
    if (! role || ! msg.member.roles.includes(role.id)) {
      channel.createMessage("Keine passende Rolle gefunden. Du musst die Rolle haben damit sie angezeigt werden kann.");
      return;
    }

    await setModeratorDefaultRoleOverride(msg.member.id, role.id);
    channel.createMessage(`Deine angezeigte Rolle ist in diesem Thread nun **${role.name}**. Du kannst sie zurücksetzen mit \`${config.prefix}role reset\`.`);
  });
};
