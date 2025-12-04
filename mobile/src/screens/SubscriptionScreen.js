import React, { useState } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, ScrollView, TextInput, Alert } from 'react-native';
import { Picker } from '@react-native-picker/picker';
import { paymentAPI } from '../api';

export default function SubscriptionScreen({ navigation }) {
  const [selectedPlan, setSelectedPlan] = useState('monthly');
  const [provider, setProvider] = useState('mpesa');
  const [phoneNumber, setPhoneNumber] = useState('');
  const [loading, setLoading] = useState(false);

  const plans = [
    { value: 'monthly', label: 'Monthly', price: 'TZS 10,000', duration: '1 month' },
    { value: 'quarterly', label: 'Quarterly', price: 'TZS 25,000', duration: '3 months' },
    { value: 'yearly', label: 'Yearly', price: 'TZS 90,000', duration: '12 months' },
  ];

  const features = [
    'Unlimited swipes',
    'Unlimited messages',
    'See who liked you',
    'Rewind last swipe',
    'Change location',
    'No ads',
    'Priority support',
  ];

  const handleSubscribe = async () => {
    if (!phoneNumber) {
      Alert.alert('Error', 'Please enter phone number');
      return;
    }

    setLoading(true);
    try {
      const response = await paymentAPI.initiateSubscription({
        plan: selectedPlan,
        provider,
        phone_number: phoneNumber,
      });

      Alert.alert('Payment Initiated', response.data.message);
      
      checkPaymentStatus(response.data.reference);
    } catch (error) {
      Alert.alert('Error', error.response?.data?.error || 'Payment failed');
      setLoading(false);
    }
  };

  const checkPaymentStatus = async (reference) => {
    const interval = setInterval(async () => {
      try {
        const response = await paymentAPI.checkStatus(reference);
        
        if (response.data.status === 'completed') {
          clearInterval(interval);
          Alert.alert('Success', 'You are now a premium member!');
          navigation.goBack();
        } else if (response.data.status === 'failed') {
          clearInterval(interval);
          Alert.alert('Payment Failed', 'Please try again');
          setLoading(false);
        }
      } catch (error) {
        console.log('Status check error:', error);
      }
    }, 3000);

    setTimeout(() => {
      clearInterval(interval);
      setLoading(false);
    }, 120000);
  };

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => navigation.goBack()}>
          <Text style={styles.backButton}>← Back</Text>
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Upgrade to Premium</Text>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Premium Features</Text>
        {features.map((feature, index) => (
          <View key={index} style={styles.featureItem}>
            <Text style={styles.checkmark}>✓</Text>
            <Text style={styles.featureText}>{feature}</Text>
          </View>
        ))}
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Choose Your Plan</Text>
        {plans.map((plan) => (
          <TouchableOpacity
            key={plan.value}
            style={[
              styles.planCard,
              selectedPlan === plan.value && styles.selectedPlan
            ]}
            onPress={() => setSelectedPlan(plan.value)}
          >
            <View style={styles.planInfo}>
              <Text style={styles.planLabel}>{plan.label}</Text>
              <Text style={styles.planDuration}>{plan.duration}</Text>
            </View>
            <Text style={styles.planPrice}>{plan.price}</Text>
          </TouchableOpacity>
        ))}
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Payment Method</Text>
        <View style={styles.pickerContainer}>
          <Picker
            selectedValue={provider}
            onValueChange={setProvider}
            style={styles.picker}
          >
            <Picker.Item label="M-Pesa" value="mpesa" />
            <Picker.Item label="TigoPesa" value="tigopesa" />
            <Picker.Item label="Airtel Money" value="airtel" />
            <Picker.Item label="Pesapal" value="pesapal" />
          </Picker>
        </View>

        <TextInput
          style={styles.input}
          placeholder="Phone Number (255...)"
          value={phoneNumber}
          onChangeText={setPhoneNumber}
          keyboardType="phone-pad"
        />
      </View>

      <TouchableOpacity 
        style={styles.subscribeButton} 
        onPress={handleSubscribe}
        disabled={loading}
      >
        <Text style={styles.subscribeButtonText}>
          {loading ? 'Processing...' : 'Subscribe Now'}
        </Text>
      </TouchableOpacity>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
  },
  header: {
    paddingTop: 50,
    paddingBottom: 20,
    paddingHorizontal: 20,
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },
  backButton: {
    fontSize: 16,
    color: '#FF6B6B',
    marginBottom: 10,
  },
  headerTitle: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#333',
  },
  section: {
    padding: 20,
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 15,
  },
  featureItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  checkmark: {
    fontSize: 20,
    color: '#4CAF50',
    marginRight: 10,
  },
  featureText: {
    fontSize: 16,
    color: '#666',
  },
  planCard: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 20,
    borderWidth: 2,
    borderColor: '#ddd',
    borderRadius: 15,
    marginBottom: 15,
  },
  selectedPlan: {
    borderColor: '#FF6B6B',
    backgroundColor: '#FFE5E5',
  },
  planInfo: {
    flex: 1,
  },
  planLabel: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
  },
  planDuration: {
    fontSize: 14,
    color: '#666',
    marginTop: 5,
  },
  planPrice: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#FF6B6B',
  },
  pickerContainer: {
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 10,
    marginBottom: 15,
    overflow: 'hidden',
  },
  picker: {
    height: 50,
  },
  input: {
    height: 50,
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 10,
    paddingHorizontal: 15,
    fontSize: 16,
  },
  subscribeButton: {
    margin: 20,
    padding: 20,
    backgroundColor: '#FF6B6B',
    borderRadius: 25,
    alignItems: 'center',
  },
  subscribeButtonText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
  },
});