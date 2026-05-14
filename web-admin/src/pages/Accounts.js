import React, { useState, useEffect } from 'react';
import { Table, Button, Modal, Form, Input, Select, Drawer, Row, Col, Statistic, Spin, Alert, Space, Tag } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined, EyeOutlined } from '@ant-design/icons';
import { accountsAPI } from '../api/client';

const Accounts = () => {
  const [accounts, setAccounts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [modalVisible, setModalVisible] = useState(false);
  const [drawerVisible, setDrawerVisible] = useState(false);
  const [selectedAccount, setSelectedAccount] = useState(null);
  const [editingId, setEditingId] = useState(null);
  const [form] = Form.useForm();

  useEffect(() => {
    fetchAccounts();
  }, []);

  const fetchAccounts = async () => {
    try {
      setLoading(true);
      const response = await accountsAPI.getList();
      setAccounts(response.data || []);
      setError(null);
    } catch (err) {
      setError('Failed to load accounts');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleShowModal = (account = null) => {
    if (account) {
      setEditingId(account.id);
      form.setFieldsValue(account);
    } else {
      setEditingId(null);
      form.resetFields();
    }
    setModalVisible(true);
  };

  const handleCloseModal = () => {
    setModalVisible(false);
    form.resetFields();
  };

  const handleSubmit = async (values) => {
    try {
      if (editingId) {
        await accountsAPI.update(editingId, values);
      } else {
        await accountsAPI.create(values);
      }
      fetchAccounts();
      handleCloseModal();
    } catch (err) {
      console.error('Failed to save account:', err);
    }
  };

  const handleDelete = async (id) => {
    Modal.confirm({
      title: 'Delete Account',
      content: 'Are you sure you want to delete this account?',
      okText: 'Yes',
      cancelText: 'No',
      onOk: async () => {
        try {
          await accountsAPI.delete(id);
          fetchAccounts();
        } catch (err) {
          console.error('Failed to delete account:', err);
        }
      },
    });
  };

  const handleViewDetails = (account) => {
    setSelectedAccount(account);
    setDrawerVisible(true);
  };

  const columns = [
    {
      title: 'Name',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: 'Type',
      dataIndex: 'account_type',
      key: 'account_type',
      render: (type) => (
        <Tag color={type === 'source' ? 'blue' : 'green'}>{type}</Tag>
      ),
    },
    {
      title: 'Status',
      dataIndex: 'enabled',
      key: 'enabled',
      render: (enabled) => (
        <Tag color={enabled ? 'success' : 'error'}>{enabled ? 'Enabled' : 'Disabled'}</Tag>
      ),
    },
    {
      title: 'Balance',
      dataIndex: 'balance',
      key: 'balance',
      render: (balance) => `$${(balance || 0).toFixed(2)}`,
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_, record) => (
        <Space>
          <Button
            type="primary"
            size="small"
            icon={<EyeOutlined />}
            onClick={() => handleViewDetails(record)}
          >
            View
          </Button>
          <Button
            type="default"
            size="small"
            icon={<EditOutlined />}
            onClick={() => handleShowModal(record)}
          >
            Edit
          </Button>
          <Button
            type="primary"
            danger
            size="small"
            icon={<DeleteOutlined />}
            onClick={() => handleDelete(record.id)}
          >
            Delete
          </Button>
        </Space>
      ),
    },
  ];

  if (loading) return <Spin size="large" />;

  return (
    <div>
      <h1>Trading Accounts</h1>
      {error && <Alert message={error} type="error" showIcon style={{ marginBottom: 16 }} />}

      <Button
        type="primary"
        icon={<PlusOutlined />}
        style={{ marginBottom: 16 }}
        onClick={() => handleShowModal()}
      >
        Add Account
      </Button>

      <Table
        columns={columns}
        dataSource={accounts}
        rowKey="id"
        pagination={{ pageSize: 10 }}
        scroll={{ x: true }}
      />

      {/* Create/Edit Modal */}
      <Modal
        title={editingId ? 'Edit Account' : 'Add Account'}
        open={modalVisible}
        onCancel={handleCloseModal}
        onOk={() => form.submit()}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
        >
          <Form.Item
            label="Account Name"
            name="name"
            rules={[{ required: true, message: 'Please input account name' }]}
          >
            <Input placeholder="My Trading Account" />
          </Form.Item>

          <Form.Item
            label="API Key"
            name="api_key"
            rules={[{ required: true, message: 'Please input API key' }]}
          >
            <Input.Password placeholder="Your API key" />
          </Form.Item>

          <Form.Item
            label="API Secret"
            name="api_secret"
            rules={[{ required: true, message: 'Please input API secret' }]}
          >
            <Input.Password placeholder="Your API secret" />
          </Form.Item>

          <Form.Item
            label="Account Type"
            name="account_type"
            rules={[{ required: true, message: 'Please select account type' }]}
          >
            <Select>
              <Select.Option value="source">Source</Select.Option>
              <Select.Option value="target">Target</Select.Option>
            </Select>
          </Form.Item>

          <Form.Item
            label="Enabled"
            name="enabled"
            initialValue={true}
            valuePropName="checked"
          >
            <Select>
              <Select.Option value={true}>Enabled</Select.Option>
              <Select.Option value={false}>Disabled</Select.Option>
            </Select>
          </Form.Item>
        </Form>
      </Modal>

      {/* Account Details Drawer */}
      <Drawer
        title={selectedAccount?.name}
        placement="right"
        onClose={() => setDrawerVisible(false)}
        open={drawerVisible}
      >
        {selectedAccount && (
          <Row gutter={[16, 16]}>
            <Col xs={24}>
              <Statistic
                title="Balance"
                value={selectedAccount.balance || 0}
                prefix="$"
              />
            </Col>
            <Col xs={24}>
              <Statistic
                title="Total Profit"
                value={selectedAccount.total_profit || 0}
                prefix="$"
              />
            </Col>
            <Col xs={24}>
              <Statistic
                title="Win Rate"
                value={selectedAccount.win_rate || 0}
                suffix="%"
              />
            </Col>
            <Col xs={24}>
              <Statistic
                title="Total Trades"
                value={selectedAccount.total_trades || 0}
              />
            </Col>
          </Row>
        )}
      </Drawer>
    </div>
  );
};

export default Accounts;
