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
    const contract = network.getContract('basic');

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
