import React, { useState, useEffect } from 'react';
import { Row, Col, Card, Statistic, Table, Spin, Alert, Tag } from 'antd';
import { ArrowUpOutlined, ArrowDownOutlined, LineChartOutlined } from '@ant-design/icons';
import { LineChart, Line, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { tradesAPI } from '../api/client';
import dayjs from 'dayjs';

const Dashboard = () => {
  const [stats, setStats] = useState(null);
  const [trades, setTrades] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const statsRes = await tradesAPI.getStats();
      const tradesRes = await tradesAPI.getList({ limit: 10, offset: 0 });
      setStats(statsRes.data);
      setTrades(tradesRes.data);
      setError(null);
    } catch (err) {
      setError('Failed to load dashboard data');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <Spin size="large" />;

  // Mock data for charts (replace with real data from API)
  const profitData = [
    { date: 'Mon', profit: 2400 },
    { date: 'Tue', profit: 1398 },
    { date: 'Wed', profit: 9800 },
    { date: 'Thu', profit: 3908 },
    { date: 'Fri', profit: 4800 },
    { date: 'Sat', profit: 3800 },
    { date: 'Sun', profit: 4300 },
  ];

  const strategyData = [
    { name: 'Strategy 1', value: 400 },
    { name: 'Strategy 2', value: 300 },
    { name: 'Strategy 3', value: 200 },
  ];

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042'];

  const columns = [
    {
      title: 'Account',
      dataIndex: 'account',
      key: 'account',
    },
    {
      title: 'Pair',
      dataIndex: 'pair',
      key: 'pair',
    },
    {
      title: 'Type',
      dataIndex: 'type',
      key: 'type',
      render: (type) => (
        <Tag color={type === 'buy' ? 'green' : 'red'}>{type.toUpperCase()}</Tag>
      ),
    },
    {
      title: 'Amount',
      dataIndex: 'amount',
      key: 'amount',
      render: (amount) => `$${amount.toFixed(2)}`,
    },
    {
      title: 'Price',
      dataIndex: 'price',
      key: 'price',
      render: (price) => `$${price.toFixed(4)}`,
    },
    {
      title: 'Time',
      dataIndex: 'timestamp',
      key: 'timestamp',
      render: (time) => dayjs(time).format('YYYY-MM-DD HH:mm:ss'),
    },
  ];

  return (
    <div>
      <h1>Dashboard</h1>
      {error && <Alert message={error} type="error" showIcon style={{ marginBottom: 24 }} />}

      {/* Key Metrics */}
      <Row gutter={[16, 16]} style={{ marginBottom: 32 }}>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Total Profit"
              value={stats?.total_profit || 0}
              prefix="$"
              valueStyle={{ color: '#3f8600' }}
              suffix={<ArrowUpOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Total Trades"
              value={stats?.total_trades || 0}
              prefix={<LineChartOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Win Rate"
              value={stats?.win_rate || 0}
              suffix="%"
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Active Accounts"
              value={stats?.active_accounts || 0}
              valueStyle={{ color: '#faad14' }}
            />
          </Card>
        </Col>
      </Row>

      {/* Charts */}
      <Row gutter={[16, 16]} style={{ marginBottom: 32 }}>
        <Col xs={24} lg={16}>
          <Card title="Profit Trend (Last 7 Days)">
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={profitData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="profit" stroke="#8884d8" />
              </LineChart>
            </ResponsiveContainer>
          </Card>
        </Col>
        <Col xs={24} lg={8}>
          <Card title="Trades by Strategy">
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={strategyData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, value }) => `${name}: ${value}`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {strategyData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </Card>
        </Col>
      </Row>

      {/* Recent Trades */}
      <Card title="Recent Trades" style={{ marginBottom: 32 }}>
        <Table
          columns={columns}
          dataSource={trades}
          pagination={{ pageSize: 10 }}
          size="small"
          scroll={{ x: true }}
        />
      </Card>
    </div>
  );
};

export default Dashboard;
