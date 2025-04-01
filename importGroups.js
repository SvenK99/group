const admin = require('firebase-admin');

// 使用服务账号初始化 Firebase
const serviceAccount = require('./sample-firebase-ai-app-93b8b-firebase-adminsdk-fbsvc-9f1c48f15d.json');  // 你的服务账户密钥文件路径

admin.initializeApp({
  credential: admin.credential.cert(serviceAccount),
});

const db = admin.firestore();

// 群组数据
const groups = [
    {
        "name": "Telegram 每日推荐｜讨论组💬",
        "link": "https://t.me/sharetgsg",
        "tags": ["资源分享", "综合讨论"],
        "category": "综合"
    },
    {
        "name": "树莓派 Raspberry Pi",
        "link": "https://t.me/raspicn",
        "tags": ["硬件开发", "树莓派", "编程"],
        "category": "技术"
    },
    {
        "name": "游戏交流",
        "link": "https://t.me/yxbymm",
        "tags": ["多人游戏", "社交", "联机"],
        "category": "游戏"
    },
    {
        "name": "黑科技软件资源分享交流群",
        "link": "https://t.me/blacktechsharing",
        "tags": ["黑科技", "软件资源", "工具"],
        "category": "技术"
    },
    {
        "name": "单机恐怖游戏总群",
        "link": "https://t.me/danjikongbu",
        "tags": ["单机游戏", "恐怖游戏", "Steam"],
        "category": "游戏"
    },
    {
        "name": "CSGO",
        "link": "https://t.me/csgocn",
        "tags": ["FPS游戏", "竞技", "CSGO"],
        "category": "游戏"
    },
    {
        "name": "動漫遊戲Cosplay群組",
        "link": "https://t.me/cosplaysharegroup",
        "tags": ["动漫", "Cosplay", "二次元"],
        "category": "二次元"
    },
    {
        "name": "加密货币与区块链讨论群",
        "link": "https://t.me/onBlockchain",
        "tags": ["加密货币", "区块链", "投资"],
        "category": "区块链"
    },
    {
        "name": "Leetcode刷题",
        "link": "https://t.me/leetcode_discuss",
        "tags": ["算法", "刷题", "面试"],
        "category": "技术"
    },
    {
        "name": "程序员资源分享社区",
        "link": "https://t.me/joinchat/FwAZpxdwmTHP2W1sPydPAQ",
        "tags": ["编程", "IT", "技术"],
        "category": "技术"
    }
];

async function importGroups() {
  const batch = db.batch();

  // 遍历数据并批量写入 Firestore
  groups.forEach(group => {
    const docRef = db.collection('groups').doc();  // 创建一个新文档，ID 自动生成
    batch.set(docRef, group);  // 批量添加数据
  });

  try {
    // 执行批量提交
    await batch.commit();
    console.log('数据导入成功！');
  } catch (error) {
    console.error('批量导入失败:', error);
  }
}

importGroups();
