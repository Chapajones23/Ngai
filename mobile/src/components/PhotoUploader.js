import React, { useState, useEffect } from 'react';
import { View, Image, TouchableOpacity, StyleSheet, Alert, FlatList } from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import Icon from 'react-native-vector-icons/Ionicons';
import { photoAPI } from '../api';

export default function PhotoUploader() {
  const [photos, setPhotos] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadPhotos();
  }, []);

  const loadPhotos = async () => {
    try {
      const response = await photoAPI.getPhotos();
      setPhotos(response.data);
    } catch (error) {
      console.log('Load photos error:', error);
    }
  };

  const pickImage = async () => {
    const permissionResult = await ImagePicker.requestMediaLibraryPermissionsAsync();
    
    if (!permissionResult.granted) {
      Alert.alert('Permission Required', 'Please grant camera roll permissions');
      return;
    }

    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      allowsEditing: true,
      aspect: [3, 4],
      quality: 0.8,
    });

    if (!result.canceled) {
      uploadPhoto(result.assets[0]);
    }
  };

  const uploadPhoto = async (image) => {
    setLoading(true);
    try {
      const extension = image.uri.split('.').pop();
      const presignedResponse = await photoAPI.getPresignedUrl(extension);
      const { presigned_url, file_url } = presignedResponse.data;

      const response = await fetch(image.uri);
      const blob = await response.blob();

      await fetch(presigned_url, {
        method: 'PUT',
        headers: {
          'Content-Type': `image/${extension}`,
        },
        body: blob,
      });

      await photoAPI.uploadPhoto({
        image_url: file_url,
        is_primary: photos.length === 0,
      });

      Alert.alert('Success', 'Photo uploaded successfully!');
      loadPhotos();
    } catch (error) {
      Alert.alert('Error', 'Failed to upload photo');
    } finally {
      setLoading(false);
    }
  };

  const deletePhoto = async (photoId) => {
    Alert.alert(
      'Delete Photo',
      'Are you sure you want to delete this photo?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Delete',
          style: 'destructive',
          onPress: async () => {
            try {
              await photoAPI.deletePhoto(photoId);
              Alert.alert('Success', 'Photo deleted');
              loadPhotos();
            } catch (error) {
              Alert.alert('Error', 'Failed to delete photo');
            }
          },
        },
      ]
    );
  };

  const renderPhoto = ({ item, index }) => (
    <View style={styles.photoContainer}>
      <Image source={{ uri: item.image_url }} style={styles.photo} />
      <TouchableOpacity 
        style={styles.deleteButton}
        onPress={() => deletePhoto(item.id)}
      >
        <Icon name="close-circle" size={30} color="#FF6B6B" />
      </TouchableOpacity>
      {item.is_primary && (
        <View style={styles.primaryBadge}>
          <Text style={styles.primaryText}>Primary</Text>
        </View>
      )}
    </View>
  );

  return (
    <View style={styles.container}>
      <FlatList
        data={photos}
        renderItem={renderPhoto}
        keyExtractor={(item) => item.id.toString()}
        horizontal
        showsHorizontalScrollIndicator={false}
        contentContainerStyle={styles.photosList}
      />
      
      {photos.length < 6 && (
        <TouchableOpacity 
          style={styles.addButton}
          onPress={pickImage}
          disabled={loading}
        >
          <Icon name="add" size={40} color="#FF6B6B" />
        </TouchableOpacity>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    marginVertical: 20,
  },
  photosList: {
    paddingHorizontal: 10,
  },
  photoContainer: {
    marginHorizontal: 5,
    position: 'relative',
  },
  photo: {
    width: 120,
    height: 160,
    borderRadius: 10,
  },
  deleteButton: {
    position: 'absolute',
    top: 5,
    right: 5,
  },
  primaryBadge: {
    position: 'absolute',
    bottom: 5,
    left: 5,
    backgroundColor: '#4CAF50',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 5,
  },
  primaryText: {
    color: '#fff',
    fontSize: 12,
    fontWeight: 'bold',
  },
  addButton: {
    width: 120,
    height: 160,
    borderRadius: 10,
    borderWidth: 2,
    borderColor: '#FF6B6B',
    borderStyle: 'dashed',
    justifyContent: 'center',
    alignItems: 'center',
    marginHorizontal: 5,
  },
});