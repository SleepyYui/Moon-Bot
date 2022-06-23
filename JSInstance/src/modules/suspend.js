const moment = require("moment");
const threads = require("../data/threads");
const utils = require("../utils");

const {THREAD_STATUS} = require("../data/constants");
const {getOrFetchChannel} = require("../utils");

module.exports = ({ bot, knex, config, commands }) => {
  if (! config.allowSuspend) return;
  // Check for threads that are scheduled to be suspended and suspend them
  async function applyScheduledSuspensions() {
    const threadsToBeSuspended = await threads.getThreadsThatShouldBeSuspended();
    for (const thread of threadsToBeSuspended) {
      if (thread.status === THREAD_STATUS.OPEN) {
        await thread.suspend();
        await thread.postSystemMessage(`**Thread suspendiert** wie von ${thread.scheduled_suspend_name} angefordert. Dieser Thread wird sich wie geschlossen verhalten bis jemand \`=unsuspend\` benutzt.`);
      }
    }
  }

  async function scheduledSuspendLoop() {
    try {
      await applyScheduledSuspensions();
    } catch (e) {
      console.error(e);
    }

    setTimeout(scheduledSuspendLoop, 2000);
  }

  scheduledSuspendLoop();

  commands.addInboxThreadCommand("suspend cancel", [], async (msg, args, thread) => {
    // Cancel timed suspend
    if (thread.scheduled_suspend_at) {
      await thread.cancelScheduledSuspend();
      thread.postSystemMessage("Geplantes Suspendieren abgebrochen.");
    } else {
      thread.postSystemMessage("Thread wurde nicht geplant suspendiert.");
    }
  });

  commands.addInboxThreadCommand("suspend", "[delay:delay]", async (msg, args, thread) => {
    if (thread.status === THREAD_STATUS.SUSPENDED) {
      thread.postSystemMessage("Thread is already suspended.");
      return;
    }
    if (args.delay) {
      const suspendAt = moment.utc().add(args.delay, "ms");
      await thread.scheduleSuspend(suspendAt.format("YYYY-MM-DD HH:mm:ss"), msg.author);

      thread.postSystemMessage(`Thread wird suspendiert in ${utils.humanizeDelay(args.delay)}. Nutze \`${config.prefix}suspend cancel\` um den Vorgang abzubrechen.`);

      return;
    }

    await thread.suspend();
    thread.postSystemMessage("**Thread Suspemdiert!** Dieser Thread wird sich wie geschlossen verhalten bis jemand `!unsuspend` benutzt.");
  }, { allowSuspended: true });

  commands.addInboxServerCommand("unsuspend", [], async (msg, args, thread) => {
    if (thread) {
      thread.postSystemMessage("Thread ist nicht Suspendiert");
      return;
    }

    thread = await threads.findSuspendedThreadByChannelId(msg.channel.id);
    if (! thread) {
      const channel = await getOrFetchChannel(bot, msg.channel.id);
      channel.createMessage("Kein Threas");
      return;
    }

    const otherOpenThread = await threads.findOpenThreadByUserId(thread.user_id);
    if (otherOpenThread) {
      thread.postSystemMessage(`Kann nicht ent-suspendieren. Der User hat bereits einen offenen Channel: <#${otherOpenThread.channel_id}>`);
      return;
    }

    await thread.unsuspend();
    thread.postSystemMessage("**Thread ent-suspendiert!**");
  });
};
