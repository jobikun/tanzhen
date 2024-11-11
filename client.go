package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"time"

	"github.com/shirou/gopsutil/cpu"
	"github.com/shirou/gopsutil/disk"
	"github.com/shirou/gopsutil/host"
	"github.com/shirou/gopsutil/mem"
	"github.com/shirou/gopsutil/net"
)

// SystemMetrics 系统指标结构
type SystemMetrics struct {
	Timestamp string                 `json:"timestamp"`
	Hostname  string                 `json:"hostname"`
	IP        string                 `json:"ip"`
	System    string                 `json:"system"`
	CPU       map[string]interface{} `json:"cpu"`
	Memory    map[string]interface{} `json:"memory"`
	Disk      []interface{}         `json:"disk"`
	Network   map[string]interface{} `json:"network"`
}

func main() {
	serverURL := os.Getenv("SERVER_URL")
	if serverURL == "" {
		serverURL = "http://localhost:5000"
	}

	interval := 60 * time.Second
	if intervalStr := os.Getenv("REPORT_INTERVAL"); intervalStr != "" {
		if d, err := time.ParseDuration(intervalStr); err == nil {
			interval = d
		}
	}

	hostname, _ := os.Hostname()
	fmt.Printf("探针客户端启动 - %s\n", hostname)
	fmt.Printf("服务器地址: %s\n", serverURL)
	fmt.Printf("上报间隔: %s\n", interval)

	for {
		metrics, err := collectMetrics()
		if err != nil {
			log.Printf("收集指标错误: %v", err)
			time.Sleep(interval)
			continue
		}

		if err := reportMetrics(serverURL, metrics); err != nil {
			log.Printf("上报指标错误: %v", err)
		} else {
			log.Printf("指标上报成功: %s", time.Now().Format("2006-01-02 15:04:05"))
		}

		time.Sleep(interval)
	}
}

// 收集系统指标
func collectMetrics() (*SystemMetrics, error) {
	hostname, err := os.Hostname()
	if err != nil {
		return nil, err
	}

	hostInfo, err := host.Info()
	if err != nil {
		return nil, err
	}

	metrics := &SystemMetrics{
		Timestamp: time.Now().Format("2006-01-02 15:04:05"),
		Hostname:  hostname,
		IP:        getLocalIP(),
		System:    hostInfo.Platform,
	}

	// CPU信息
	cpuPercent, err := cpu.Percent(time.Second, true)
	if err == nil {
		metrics.CPU = map[string]interface{}{
			"percent": cpuPercent,
			"count":   len(cpuPercent),
		}
	}

	// 内存信息
	if vmem, err := mem.VirtualMemory(); err == nil {
		metrics.Memory = map[string]interface{}{
			"total":   vmem.Total,
			"used":    vmem.Used,
			"percent": vmem.UsedPercent,
		}
	}

	// 磁盘信息
	partitions, err := disk.Partitions(false)
	if err == nil {
		var diskInfo []interface{}
		for _, partition := range partitions {
			usage, err := disk.Usage(partition.Mountpoint)
			if err != nil {
				continue
			}
			diskInfo = append(diskInfo, map[string]interface{}{
				"device":     partition.Device,
				"mountpoint": partition.Mountpoint,
				"total":      usage.Total,
				"used":       usage.Used,
				"free":       usage.Free,
				"percent":    usage.UsedPercent,
			})
		}
		metrics.Disk = diskInfo
	}

	// 网络信息
	if netIO, err := net.IOCounters(false); err == nil && len(netIO) > 0 {
		metrics.Network = map[string]interface{}{
			"bytes_sent":   netIO[0].BytesSent,
			"bytes_recv":   netIO[0].BytesRecv,
			"packets_sent": netIO[0].PacketsSent,
			"packets_recv": netIO[0].PacketsRecv,
		}
	}

	return metrics, nil
}

// 上报指标到服务器
func reportMetrics(serverURL string, metrics *SystemMetrics) error {
	data, err := json.Marshal(metrics)
	if err != nil {
		return err
	}

	req, err := http.NewRequest("POST", serverURL+"/report", bytes.NewBuffer(data))
	if err != nil {
		return err
	}

	// 添加密钥到请求头
	clientSecret := os.Getenv("CLIENT_SECRET")
	if clientSecret == "" {
		clientSecret = "your-secret-key-here"  // 默认密钥
	}
	req.Header.Set("X-Client-Secret", clientSecret)
	req.Header.Set("Content-Type", "application/json")

	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		return err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return fmt.Errorf("server returned status code: %d", resp.StatusCode)
	}

	return nil
}

// 获取本机IP
func getLocalIP() string {
	addrs, err := net.Interfaces()
	if err != nil {
		return "unknown"
	}

	for _, addr := range addrs {
		if addr.Flags&net.FlagUp == 0 {
			continue
		}
		if addr.Flags&net.FlagLoopback != 0 {
			continue
		}
		return addr.HardwareAddr
	}

	return "unknown"
} 