const path = require("path");
const fs = require("fs");
const {promisify} = require("util");
const utils = require("../utils");
const { getPrettyVersion } = require("../botVersion");

const access = promisify(fs.access);
const readFile = promisify(fs.readFile);

const GIT_DIR = path.join(__dirname, "..", "..", ".git");

module.exports = ({ bot, knex, config, commands }) => {
  commands.addInboxServerCommand("version", [], async (msg, args, thread) => {
    let response = `YuMail Version: ${getPrettyVersion()}`;

    utils.postSystemMessageWithFallback(msg.channel, thread, response);
  });
};
