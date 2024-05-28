# 药物研发全流程的数据共享平台

## 前提条件

1. **安装Docker和Docker Compose**
2. **安装Hyperledger Fabric二进制文件和示例**
3. **安装Go编程语言**
4. **安装Node.js和npm**

## 步骤详解

### 第一步：设置Hyperledger Fabric网络

1. **克隆Hyperledger Fabric示例仓库**

    ```bash
    git clone https://github.com/hyperledger/fabric-samples.git
    cd fabric-samples/test-network
    ```

2. **生成加密材料和通道配置**

    ```bash
    ./network.sh up createChannel -c mychannel -ca
    ./network.sh deployCC -ccn basic -ccp ../asset-transfer-basic/chaincode-go -ccl go
    ```

    上述命令将：
    - 启动网络。
    - 创建名为`mychannel`的通道。
    - 部署Hyperledger Fabric示例中的基本链码。

### 第二步：修改配置以使用Kafka共识机制

1. **修改`configtx.yaml`文件**

    在`fabric-samples/test-network/configtx/`目录下找到并编辑`configtx.yaml`文件，将Orderer类型修改为Kafka。

    ```yaml
    Profiles:
      TwoOrgsOrdererGenesis:
        Orderer:
          OrdererType: kafka
          Kafka:
            Brokers:
              - kafka0:9092
              - kafka1:9092
              - kafka2:9092
          Addresses:
            - orderer.example.com:7050
          BatchTimeout: 2s
          BatchSize:
            MaxMessageCount: 10
            AbsoluteMaxBytes: 99 MB
            PreferredMaxBytes: 512 KB
          Organizations:
            - *OrdererOrg
          Policies:
            Readers:
              Type: ImplicitMeta
              Rule: ANY Readers
            Writers:
              Type: ImplicitMeta
              Rule: ANY Writers
            Admins:
              Type: ImplicitMeta
              Rule: MAJORITY Admins
        Consortiums:
          SampleConsortium:
            Organizations:
              - *Org1
              - *Org2
    ```

2. **设置Kafka和Zookeeper服务**

    在`fabric-samples/test-network`目录下添加一个`docker-compose-kafka.yaml`文件，并添加以下内容：

    ```yaml
    version: '2'

    networks:
      fabric_net:

    services:
      zookeeper0:
        image: wurstmeister/zookeeper:3.4.6
        ports:
          - "2181:2181"
        environment:
          ZOO_MY_ID: 1
          ZOO_SERVERS: server.1=zookeeper0:2888:3888;2181,server.2=zookeeper1:2888:3888;2181,server.3=zookeeper2:2888:3888;2181
        networks:
          - fabric_net

      zookeeper1:
        image: wurstmeister/zookeeper:3.4.6
        ports:
          - "2182:2181"
        environment:
          ZOO_MY_ID: 2
          ZOO_SERVERS: server.1=zookeeper0:2888:3888;2181,server.2=zookeeper1:2888:3888;2181,server.3=zookeeper2:2888:3888;2181
        networks:
          - fabric_net

      zookeeper2:
        image: wurstmeister/zookeeper:3.4.6
        ports:
          - "2183:2181"
        environment:
          ZOO_MY_ID: 3
          ZOO_SERVERS: server.1=zookeeper0:2888:3888;2181,server.2=zookeeper1:2888:3888;2181,server.3=zookeeper2:2888:3888;2181
        networks:
          - fabric_net

      kafka0:
        image: wurstmeister/kafka:2.11-2.0.0
        ports:
          - "9092:9092"
        environment:
          KAFKA_BROKER_ID: 0
          KAFKA_ZOOKEEPER_CONNECT: zookeeper0:2181,zookeeper1:2181,zookeeper2:2181
          KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka0:9092
          KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 3
        networks:
          - fabric_net

      kafka1:
        image: wurstmeister/kafka:2.11-2.0.0
        ports:
          - "9093:9092"
        environment:
          KAFKA_BROKER_ID: 1
          KAFKA_ZOOKEEPER_CONNECT: zookeeper0:2181,zookeeper1:2181,zookeeper2:2181
          KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka1:9092
          KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 3
        networks:
          - fabric_net

      kafka2:
        image: wurstmeister/kafka:2.11-2.0.0
        ports:
          - "9094:9092"
        environment:
          KAFKA_BROKER_ID: 2
          KAFKA_ZOOKEEPER_CONNECT: zookeeper0:2181,zookeeper1:2181,zookeeper2:2181
          KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka2:9092
          KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 3
        networks:
          - fabric_net
    ```

3. **启动Kafka和Zookeeper服务**

    运行以下命令启动Kafka和Zookeeper服务：

    ```bash
    docker-compose -f docker-compose-kafka.yaml up -d
    ```

4. **生成加密材料和通道配置**

    使用`cryptogen`和`configtxgen`工具生成必要的加密材料和通道配置：

    ```bash
    cryptogen generate --config=./crypto-config.yaml
    configtxgen -profile TwoOrgsOrdererGenesis -outputBlock ./channel-artifacts/genesis.block
    configtxgen -profile TwoOrgsChannel -outputCreateChannelTx ./channel-artifacts/channel.tx -channelID mychannel
    ```

5. **启动Fabric网络**

    使用修改后的配置启动网络：

    ```bash
    docker-compose -f docker-compose-kafka.yaml -f docker-compose-cli.yaml up -d
    ```

    确保网络启动并运行，然后创建并加入通道：

    ```bash
    docker exec cli ./scripts/script.sh mychannel
    ```

### 第三步：部署链码

按照之前的步骤部署链码：

    ```bash
    ./network.sh deployCC -ccn custom -ccp ../custom-chaincode/chaincode-go -ccl go 
    ```

### 第四步：设置Node.js应用程序

1. **创建新的目录并初始化项目**

    ```bash
    mkdir fabric-app
    cd fabric-app
    npm init -y
    ```

2. **安装必要的依赖**

    ```bash
    npm install express body-parser fabric-network
    ```

3. **创建应用程序文件**

    在`fabric-app`目录中创建`app.js`文件并添加以下内容：

    ```javascript
    const express = require('express');
    const bodyParser = require('body-parser');
    const { Gateway, Wallets } = require('fabric-network');
    const path = require('path');
    const fs = require('fs');

    const app = express();
    app.use(bodyParser.json());

    const ccpPath = path.resolve(__dirname, '..', 'fabric-samples', 'test-network', 'organizations', 'peerOrganizations', 'org1.example.com', 'connection-org1.json');
    const ccp = JSON.parse(fs.readFileSync(ccpPath, 'utf8'));

    async function main() {
        const walletPath = path.join(process.cwd(), 'wallet');
        const wallet = await Wallets.newFileSystemWallet(walletPath);
        const gateway = new Gateway();
        await gateway.connect(ccp, {
            wallet,
            identity: 'appUser',
            discovery: { enabled: true, asLocalhost: true }
        });

        const network = await gateway.getNetwork('mychannel');
        const contract = network.getContract('custom'); // 使用自定义链码

        app.post('/createAsset', async (req, res) => {
            const { key, value } = req.body;
            await contract.submitTransaction('createAsset', key, value);
            res.send('Transaction has been submitted');
        });

        app.get('/readAsset', async (req, res) => {
            const { key } = req.query;
            const result = await contract.evaluateTransaction('readAsset', key);
            res.send(`Asset: ${result.toString()}`);
        });

        app.listen(3000, () => {
            console.log('Server is running on port 3000');
        });
    }

    main();
    ```

### 第五步：运行Node.js应用程序

确保Hyperledger Fabric网络已经启动，然后运行Node.js应用程序：

    ```bash
    cd fabric-app
    node app.js
    ```

### 第六部：验证

1. **创建资产**

    ```bash
    curl -X POST http://localhost:3000/createAsset -H "Content-Type: application/json" -d '{"key":"asset1","value":"value1"}'
    ```

2. **读取资产**

    ```bash
    curl -X GET "http://localhost:3000/readAsset?key=asset1"
    ```