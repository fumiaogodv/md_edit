# TCP 三次握手

建立 TCP 连接前需要三次握手确认双方收发能力。

## 握手过程

1. 客户端发送 SYN
2. 服务端回复 SYN + ACK
3. 客户端发送 ACK

## 状态转换

> 三次握手保证了连接的可靠性，但也引入了延迟。

## 代码示例

```javascript
const net = require('net')
const server = net.createServer((socket) => {
  console.log('客户端已连接')
})
server.listen(8080)
```

## 相关公式

网络吞吐量估算：

$$
\text{Throughput} = \frac{\text{Window Size}}{\text{RTT}}
$$
