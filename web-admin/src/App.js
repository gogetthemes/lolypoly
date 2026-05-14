import React, { useState, useEffect } from 'react';
import { Layout, Menu, Button, Badge, Dropdown, Avatar, Space } from 'antd';
import {
  DashboardOutlined,
  AccountBookOutlined,
  LineChartOutlined,
  SettingOutlined,
  LogoutOutlined,
  PoweroffOutlined,
  ReloadOutlined,
  PlayCircleOutlined,
} from '@ant-design/icons';
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import Accounts from './pages/Accounts';
import Strategies from './pages/Strategies';
import Analytics from './pages/Analytics';
import Settings from './pages/Settings';
import { botAPI } from './api/client';
import './App.css';

const { Header, Content, Sider } = Layout;

function App() {
  const [collapsed, setCollapsed] = useState(false);
  const [botStatus, setBotStatus] = useState('stopped');
  const [botLoading, setBotLoading] = useState(false);

  useEffect(() => {
    fetchBotStatus();
    const interval = setInterval(fetchBotStatus, 5000);
    return () => clearInterval(interval);
  }, []);

  const fetchBotStatus = async () => {
    try {
      const response = await botAPI.getStatus();
      setBotStatus(response.data.status || 'stopped');
    } catch (error) {
      console.error('Failed to fetch bot status:', error);
    }
  };

  const handleBotControl = async (action) => {
    setBotLoading(true);
    try {
      if (action === 'start') await botAPI.start();
      else if (action === 'stop') await botAPI.stop();
      else if (action === 'restart') await botAPI.restart();
      fetchBotStatus();
    } catch (error) {
      console.error(`Failed to ${action} bot:`, error);
    }
    setBotLoading(false);
  };

  const menuItems = [
    {
      key: '/',
      icon: <DashboardOutlined />,
      label: <Link to="/">Dashboard</Link>,
    },
    {
      key: '/accounts',
      icon: <AccountBookOutlined />,
      label: <Link to="/accounts">Accounts</Link>,
    },
    {
      key: '/strategies',
      icon: <LineChartOutlined />,
      label: <Link to="/strategies">Strategies</Link>,
    },
    {
      key: '/analytics',
      icon: <LineChartOutlined />,
      label: <Link to="/analytics">Analytics</Link>,
    },
    {
      key: '/settings',
      icon: <SettingOutlined />,
      label: <Link to="/settings">Settings</Link>,
    },
  ];

  const userMenu = [
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: 'Logout',
    },
  ];

  return (
    <BrowserRouter>
      <Layout style={{ minHeight: '100vh' }}>
        <Sider
          collapsible
          collapsed={collapsed}
          onCollapse={setCollapsed}
          theme="dark"
          style={{ background: '#001529' }}
        >
          <div className="logo">
            <h2>{collapsed ? 'LP' : 'LolyPoly'}</h2>
          </div>
          <Menu theme="dark" defaultSelectedKeys={['/']} mode="inline" items={menuItems} />
        </Sider>

        <Layout>
          <Header style={{ background: '#fff', padding: '0 24px', boxShadow: '0 2px 8px rgba(0,0,0,0.1)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Space size="large">
                <Badge
                  status={botStatus === 'running' ? 'success' : 'error'}
                  text={`Bot: ${botStatus.toUpperCase()}`}
                />
              </Space>

              <Space>
                <Button
                  type="primary"
                  icon={<PlayCircleOutlined />}
                  loading={botLoading}
                  onClick={() => handleBotControl('start')}
                  disabled={botStatus === 'running'}
                >
                  Start
                </Button>
                <Button
                  danger
                  icon={<PoweroffOutlined />}
                  loading={botLoading}
                  onClick={() => handleBotControl('stop')}
                  disabled={botStatus === 'stopped'}
                >
                  Stop
                </Button>
                <Button
                  icon={<ReloadOutlined />}
                  loading={botLoading}
                  onClick={() => handleBotControl('restart')}
                >
                  Restart
                </Button>

                <Dropdown menu={{ items: userMenu }}>
                  <Avatar style={{ backgroundColor: '#87d068' }}>U</Avatar>
                </Dropdown>
              </Space>
            </div>
          </Header>

          <Content style={{ margin: '24px' }}>
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/accounts" element={<Accounts />} />
              <Route path="/strategies" element={<Strategies />} />
              <Route path="/analytics" element={<Analytics />} />
              <Route path="/settings" element={<Settings />} />
            </Routes>
          </Content>
        </Layout>
      </Layout>
    </BrowserRouter>
  );
}

export default App;
