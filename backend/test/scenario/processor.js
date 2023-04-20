const { Client } = require('pg');
const fs = require('fs').promises;

module.exports = {
    selectTeam,
    getTeams,
    getRandomSleep,
    getRandomOpinion,
    recvOpinion,
    tearDown
}

const db_config = {
    host: process.env.POSTGRES_HOST,
    port: process.env.POSTGRES_PORT,
    user: process.env.POSTGRES_USER,
    password: process.env.POSTGRES_PASSWORD,
    database: process.env.POSTGRES_DATABASE,
}

const path = {
    dummy_opinion: './test/scenario/dummy/opinion.csv',
    dummy_user: './test/scenario/dummy/user.csv',
}


function getTeams(userContext, data, callback) {
    if (data.action == "initJoinResult") {
        userContext.vars.teams = data.teams
        return callback(null, userContext);
    }
}


// CSV 파일에서 랜덤으로 하나의 행을 선택하는 함수
async function getRandomOpinion(userContext, events, done) {
    const csv = await fs.readFile(path.dummy_opinion, 'utf-8');
    const rows = csv.trim().split('\n').slice(1); // 헤더 제외한 행들만 추출
    const randomIndex = Math.floor(Math.random() * rows.length);
    const randomRow = rows[randomIndex];
    const [round, opinion] = randomRow.split(',');

    userContext.vars.opinion = opinion;

    return done();
}


function getRandomSleep(userContext, events, done) {
    // get 1~5 random
    const randomAmount = Math.floor(Math.random() * 5) + 1;
    userContext.vars.randomAmount = randomAmount;

    return done();
}

// ws custom capture handler의 핵심은 send에 대응하는 단 하나의 recv에 대해서만 callback을 부르는 것이다.
// broadcast 등 다른 메세지에 대해서는 callback을 부르지 않는다.
// 만약 부르면 Callback already called! 에러가 발생한다.
function recvOpinion(userContext, data, callback) {
    if (data.action == "recvOpinion" && data.nickname == userContext.vars.nickname) {
        userContext.vars.opinion = data.opinion;
        userContext.vars.other = data.nickname;
        return callback(null, userContext);
    }
}


function selectTeam(userContext, events, done) {
    var teams = userContext.vars.teams;
    var selectedTeam = teams[Math.floor(Math.random() * teams.length)];
    userContext.vars.selectedTeam = selectedTeam;

    return done();
}


// 비동기 함수는 반드시 Promise 기반으로 동작시켜야 함
async function tearDown(userContext, events, done) {
    // do any cleanup here

    const client = new Client(db_config);

    await client.connect()
        .then(() => {
            userContext.vars.client = client;
            console.log("[Test::Artillery::tearDown] Client is connected.")
        })
        .catch((err) => {
            console.log("[Test::Artillery::tearDown] Client connection failed.")
            console.log(err);
        });

    await client.query('DELETE FROM Opinion')
        .then(() => {
            console.log('[Test::Artillery::tearDown] Opinion table is deleted.');
        })
        .catch((err) => {
            console.log('[Test::Artillery::tearDown] Failed to delete Opinion table.');
            console.log(err);
        });

    await client.end()
        .then(() => { console.log('[Test::Artillery::tearDown] Client is disconnected.') })
        .catch((err) => { console.log(err) });


    return done();
}

