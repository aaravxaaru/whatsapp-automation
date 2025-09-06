import makeWASocket, { useMultiFileAuthState } from "@whiskeysockets/baileys"
import P from "pino"
import express from "express"

const app = express()
app.use(express.json())

let sock

async function startSock() {
    const { state, saveCreds } = await useMultiFileAuthState("auth_info") // creds.json save hoga
    sock = makeWASocket({
        auth: state,
        printQRInTerminal: true,   // ✅ Render logs me QR dikhega
        logger: P({ level: "silent" })
    })

    sock.ev.on("creds.update", saveCreds)

    sock.ev.on("connection.update", (update) => {
        const { connection } = update
        if (connection === "open") {
            console.log("✅ WhatsApp connected, creds.json saved in auth_info/")
        }
    })
}

// ✅ API to send message
app.post("/send", async (req, res) => {
    try {
        const { number, message } = req.body
        if (!sock) return res.status(500).send("❌ WhatsApp not connected")

        const jid = number.includes("@s.whatsapp.net") ? number : number + "@s.whatsapp.net"
        await sock.sendMessage(jid, { text: message })

        res.send(`✅ Message sent to ${number}`)
    } catch (err) {
        console.error(err)
        res.status(500).send("❌ Error sending message")
    }
})

const PORT = process.env.PORT || 5000
app.listen(PORT, () => console.log(`🚀 Server running on ${PORT}`))

startSock()
