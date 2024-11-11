package main

import (
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"path/filepath"
	"sync"
	"time"

	"github.com/gin-contrib/sessions"
	"github.com/gin-contrib/sessions/cookie"
	"github.com/gin-gonic/gin"
)

// ClientData 存储客户端数据
type ClientData struct {
	Timestamp string                 `json:"timestamp"`
	Hostname  string                 `json:"hostname"`
	IP        string                 `json:"ip"`
	System    string                 `json:"system"`
	CPU       map[string]interface{} `json:"cpu"`
	Memory    map[string]interface{} `json:"memory"`
	Disk      []interface{}         `json:"disk"`
	Network   map[string]interface{} `json:"network"`
}

// 全局变量
var (
	clientsData     = make(map[string][]ClientData)
	clientsLastSeen = make(map[string]time.Time)
	dataLock        sync.RWMutex
	adminPassword   = sha256.Sum256([]byte("admin123"))
	clientSecret    = "your-secret-key-here"  // 客户端连接密钥
)

func main() {
	r := gin.Default()

	// 设置session中间件
	store := cookie.NewStore([]byte("secret-key"))
	r.Use(sessions.Sessions("session", store))

	// 设置HTML模板
	r.LoadHTMLGlob("templates/*")

	// 路由设置
	r.GET("/", authRequired, handleIndex)
	r.GET("/login", handleLoginPage)
	r.POST("/login", handleLogin)
	r.GET("/logout", handleLogout)
	r.POST("/report", handleReport)
	r.GET("/clients", authRequired, handleGetClients)
	r.GET("/client/:ip", authRequired, handleGetClientData)
	r.GET("/change-password", authRequired, handleChangePasswordPage)
	r.POST("/change-password", authRequired, handleChangePassword)

	// 启动服务器
	log.Fatal(r.Run(":5000"))
}

// 中间件：认证检查
func authRequired(c *gin.Context) {
	session := sessions.Default(c)
	if session.Get("logged_in") != true {
		c.Redirect(http.StatusFound, "/login")
		c.Abort()
		return
	}
	c.Next()
}

// 处理登录页面
func handleLoginPage(c *gin.Context) {
	c.HTML(http.StatusOK, "login.html", nil)
}

// 处理登录请求
func handleLogin(c *gin.Context) {
	username := c.PostForm("username")
	password := c.PostForm("password")

	if username != "admin" {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "Invalid credentials"})
		return
	}

	hashedPassword := sha256.Sum256([]byte(password))
	if hashedPassword != adminPassword {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "Invalid credentials"})
		return
	}

	session := sessions.Default(c)
	session.Set("logged_in", true)
	session.Set("username", username)
	session.Save()

	c.Redirect(http.StatusFound, "/")
}

// 处理登出请求
func handleLogout(c *gin.Context) {
	session := sessions.Default(c)
	session.Clear()
	session.Save()
	c.Redirect(http.StatusFound, "/login")
}

// 处理客户端上报数据
func handleReport(c *gin.Context) {
	// 验证密钥
	if c.GetHeader("X-Client-Secret") != clientSecret {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "Invalid client secret"})
		return
	}

	var data ClientData
	if err := c.BindJSON(&data); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	dataLock.Lock()
	clientsData[data.IP] = append(clientsData[data.IP], data)
	if len(clientsData[data.IP]) > 100 {
		clientsData[data.IP] = clientsData[data.IP][1:]
	}
	clientsLastSeen[data.IP] = time.Now()
	dataLock.Unlock()

	saveToFile(data)
	c.JSON(http.StatusOK, gin.H{"status": "success"})
}

// 保存数据到文件
func saveToFile(data ClientData) {
	dateStr := time.Now().Format("20060102")
	filename := filepath.Join("logs", fmt.Sprintf("probe_%s.json", dateStr))

	os.MkdirAll("logs", 0755)

	f, err := os.OpenFile(filename, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
	if err != nil {
		log.Printf("Error opening file: %v", err)
		return
	}
	defer f.Close()

	encoder := json.NewEncoder(f)
	if err := encoder.Encode(data); err != nil {
		log.Printf("Error encoding data: %v", err)
	}
}

// 获取所有客户端列表
func handleGetClients(c *gin.Context) {
	dataLock.RLock()
	defer dataLock.RUnlock()

	clients := make([]map[string]interface{}, 0)
	for ip, lastSeen := range clientsLastSeen {
		if len(clientsData[ip]) == 0 {
			continue
		}

		latestData := clientsData[ip][len(clientsData[ip])-1]
		status := "离线"
		if time.Since(lastSeen) < 3*time.Minute {
			status = "在线"
		}

		clients = append(clients, map[string]interface{}{
			"ip":        ip,
			"hostname":  latestData.Hostname,
			"system":    latestData.System,
			"last_seen": lastSeen.Format("2006-01-02 15:04:05"),
			"status":    status,
		})
	}

	c.JSON(http.StatusOK, clients)
}

// 获取指定客户端详细数据
func handleGetClientData(c *gin.Context) {
	ip := c.Param("ip")

	dataLock.RLock()
	defer dataLock.RUnlock()

	if data, exists := clientsData[ip]; exists && len(data) > 0 {
		c.JSON(http.StatusOK, data[len(data)-1])
		return
	}

	c.JSON(http.StatusNotFound, gin.H{"error": "Client not found"})
}

// 处理主页
func handleIndex(c *gin.Context) {
	session := sessions.Default(c)
	username := session.Get("username")
	c.HTML(http.StatusOK, "index.html", gin.H{
		"username": username,
	})
}

// 处理修改密码页面
func handleChangePasswordPage(c *gin.Context) {
	c.HTML(http.StatusOK, "change_password.html", nil)
}

// 处理修改密码请求
func handleChangePassword(c *gin.Context) {
	oldPassword := c.PostForm("old_password")
	newPassword := c.PostForm("new_password")
	confirmPassword := c.PostForm("confirm_password")

	if newPassword != confirmPassword {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Passwords do not match"})
		return
	}

	hashedOldPassword := sha256.Sum256([]byte(oldPassword))
	if hashedOldPassword != adminPassword {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "Invalid old password"})
		return
	}

	adminPassword = sha256.Sum256([]byte(newPassword))
	c.Redirect(http.StatusFound, "/")
} 