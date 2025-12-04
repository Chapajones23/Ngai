import React, { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet, Alert, ScrollView } from 'react-native';
import { Picker } from '@react-native-picker/picker';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { paymentAPI } from '../../api';

export default function PaymentScreen({ navigation, route }) {
  const { registrationData } = route.params;
  const [provider, setProvider] = useState('mpesa');
  const [phoneNumber, setPhoneNumber] = useState('');
  const [loading, setLoading] = useState(false);
  const [paymentReference, setPaymentReference] = useState(null);

  const handlePayment = async () => {
    if (!phoneNumber) {
      Alert.alert('Error', 'Please enter phone number');
      return;
    }

    setLoading(true);
    try {
      const response = await paymentAPI.initiateRegistration({
        provider,
        phone_number: phoneNumber,
        registration_data: registrationData,
      });

      setPaymentReference(response.data.reference);
      Alert.alert('Payment Initiated', response.data.message);
      
      checkPaymentStatus(response.data.reference);
    } catch (error) {
      Alert.alert('Payment Failed', error.response?.data?.error || 'Something went wrong');
      setLoading(false);
    }
  };

  const checkPaymentStatus = async (reference) => {
    const interval = setInterval(async () => {
      try {
        const response = await paymentAPI.checkStatus(reference);
        
        if (response.data.status === 'completed') {
          clearInterval(interval);
          Alert.alert('Success', 'Payment completed! You can now login.');
          navigation.navigate('Login');
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
    <ScrollView contentContainerStyle={styles.container}>
      <Text style={styles.title}>Registration Payment</Text>
      <Text style={styles.subtitle}>Complete payment to register</Text>
      <Text style={styles.amount}>Amount: TZS 10,000</Text>

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

      <TouchableOpacity 
        style={styles.button} 
        onPress={handlePayment}
        disabled={loading}
      >
        <Text style={styles.buttonText}>{loading ? 'Processing...' : 'Pay Now'}</Text>
      </TouchableOpacity>

      {paymentReference && (
        <View style={styles.referenceContainer}>
          <Text style={styles.referenceText}>Reference: {paymentReference}</Text>
          <Text style={styles.statusText}>Waiting for payment confirmation...</Text>
        </View>
      )}

      <TouchableOpacity onPress={() => navigation.goBack()}>
        <Text style={styles.linkText}>Go Back</Text>
      </TouchableOpacity>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flexGrow: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
    backgroundColor: '#fff',
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#FF6B6B',
    marginBottom: 10,
  },
  subtitle: {
    fontSize: 16,
    color: '#666',
    marginBottom: 10,
  },
  amount: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 30,
  },
  input: {
    width: '100%',
    height: 50,
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 25,
    paddingHorizontal: 20,
    marginBottom: 15,
    fontSize: 16,
  },
  pickerContainer: {
    width: '100%',
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 25,
    marginBottom: 15,
    overflow: 'hidden',
  },
  picker: {
    height: 50,
  },
  button: {
    width: '100%',
    height: 50,
    backgroundColor: '#FF6B6B',
    borderRadius: 25,
    justifyContent: 'center',
    alignItems: 'center',
    marginTop: 10,
  },
  buttonText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
  },
  referenceContainer: {
    marginTop: 30,
    padding: 15,
    backgroundColor: '#f0f0f0',
    borderRadius: 10,
    width: '100%',
  },
  referenceText: {
    fontSize: 14,
    color: '#333',
    marginBottom: 5,
  },
  statusText: {
    fontSize: 14,
    color: '#666',
    fontStyle: 'italic',
  },
  linkText: {
    marginTop: 20,
    color: '#FF6B6B',
    fontSize: 16,
  },
});