import React, { useState, useEffect, useRef } from 'react';
import { View, Text, Image, StyleSheet, TouchableOpacity, Alert } from 'react-native';
import Swiper from 'react-native-deck-swiper';
import Icon from 'react-native-vector-icons/Ionicons';
import { swipeAPI } from '../api';

export default function SwipeScreen() {
  const [suggestions, setSuggestions] = useState([]);
  const [loading, setLoading] = useState(true);
  const swiperRef = useRef(null);

  useEffect(() => {
    loadSuggestions();
  }, []);

  const loadSuggestions = async () => {
    try {
      const response = await swipeAPI.getSuggestions();
      setSuggestions(response.data);
    } catch (error) {
      Alert.alert('Error', 'Failed to load suggestions');
    } finally {
      setLoading(false);
    }
  };

  const handleSwipe = async (action, cardIndex) => {
    const user = suggestions[cardIndex];
    
    try {
      const response = await swipeAPI.swipe({
        to_user_id: user.id,
        action
      });

      if (response.data.is_match) {
        Alert.alert('Match! 💕', `You matched with ${user.username}!`);
      }
    } catch (error) {
      console.log('Swipe error:', error);
    }
  };

  const renderCard = (card) => {
    if (!card) return null;

    return (
      <View style={styles.card}>
        <Image 
          source={{ uri: card.photos?.[0]?.image_url || 'https://via.placeholder.com/400' }}
          style={styles.cardImage}
        />
        <View style={styles.cardInfo}>
          <Text style={styles.cardName}>{card.username}, {calculateAge(card.date_of_birth)}</Text>
          <Text style={styles.cardBio}>{card.bio || 'No bio yet'}</Text>
          {card.interests && card.interests.length > 0 && (
            <View style={styles.interestsContainer}>
              {card.interests.slice(0, 3).map((interest, index) => (
                <View key={index} style={styles.interestTag}>
                  <Text style={styles.interestText}>{interest}</Text>
                </View>
              ))}
            </View>
          )}
        </View>
      </View>
    );
  };

  const calculateAge = (dateOfBirth) => {
    if (!dateOfBirth) return '?';
    const today = new Date();
    const birthDate = new Date(dateOfBirth);
    let age = today.getFullYear() - birthDate.getFullYear();
    const m = today.getMonth() - birthDate.getMonth();
    if (m < 0 || (m === 0 && today.getDate() < birthDate.getDate())) {
      age--;
    }
    return age;
  };

  if (loading) {
    return (
      <View style={styles.centered}>
        <Text>Loading...</Text>
      </View>
    );
  }

  if (suggestions.length === 0) {
    return (
      <View style={styles.centered}>
        <Text style={styles.emptyText}>No more profiles</Text>
        <TouchableOpacity style={styles.reloadButton} onPress={loadSuggestions}>
          <Text style={styles.reloadButtonText}>Reload</Text>
        </TouchableOpacity>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Ngai</Text>
      </View>

      <Swiper
        ref={swiperRef}
        cards={suggestions}
        renderCard={renderCard}
        onSwipedLeft={(cardIndex) => handleSwipe('dislike', cardIndex)}
        onSwipedRight={(cardIndex) => handleSwipe('like', cardIndex)}
        onSwipedTop={(cardIndex) => handleSwipe('superlike', cardIndex)}
        cardIndex={0}
        backgroundColor={'transparent'}
        stackSize={3}
        stackSeparation={15}
        overlayLabels={{
          left: {
            title: 'NOPE',
            style: { label: styles.overlayLabel, wrapper: styles.overlayWrapper }
          },
          right: {
            title: 'LIKE',
            style: { label: styles.overlayLabel, wrapper: styles.overlayWrapper }
          },
          top: {
            title: 'SUPER LIKE',
            style: { label: styles.overlayLabel, wrapper: styles.overlayWrapper }
          }
        }}
        animateOverlayLabelsOpacity
        animateCardOpacity
        infinite={false}
        onSwipedAll={loadSuggestions}
      />

      <View style={styles.buttonsContainer}>
        <TouchableOpacity 
          style={[styles.actionButton, styles.dislikeButton]}
          onPress={() => swiperRef.current.swipeLeft()}
        >
          <Icon name="close" size={30} color="#FF6B6B" />
        </TouchableOpacity>

        <TouchableOpacity 
          style={[styles.actionButton, styles.superLikeButton]}
          onPress={() => swiperRef.current.swipeTop()}
        >
          <Icon name="star" size={25} color="#4FC3F7" />
        </TouchableOpacity>

        <TouchableOpacity 
          style={[styles.actionButton, styles.likeButton]}
          onPress={() => swiperRef.current.swipeRight()}
        >
          <Icon name="heart" size={30} color="#4CAF50" />
        </TouchableOpacity>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  centered: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  header: {
    paddingTop: 50,
    paddingBottom: 20,
    alignItems: 'center',
  },
  headerTitle: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#FF6B6B',
  },
  card: {
    height: '75%',
    borderRadius: 20,
    backgroundColor: '#fff',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.2,
    shadowRadius: 8,
    elevation: 5,
  },
  cardImage: {
    flex: 1,
    borderTopLeftRadius: 20,
    borderTopRightRadius: 20,
  },
  cardInfo: {
    padding: 20,
  },
  cardName: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 10,
  },
  cardBio: {
    fontSize: 16,
    color: '#666',
    marginBottom: 15,
  },
  interestsContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
  },
  interestTag: {
    backgroundColor: '#FFE5E5',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 15,
    marginRight: 8,
    marginBottom: 8,
  },
  interestText: {
    color: '#FF6B6B',
    fontSize: 14,
  },
  buttonsContainer: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: 20,
  },
  actionButton: {
    width: 60,
    height: 60,
    borderRadius: 30,
    justifyContent: 'center',
    alignItems: 'center',
    marginHorizontal: 15,
    backgroundColor: '#fff',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.2,
    shadowRadius: 4,
    elevation: 3,
  },
  dislikeButton: {
    borderWidth: 2,
    borderColor: '#FF6B6B',
  },
  superLikeButton: {
    borderWidth: 2,
    borderColor: '#4FC3F7',
  },
  likeButton: {
    borderWidth: 2,
    borderColor: '#4CAF50',
  },
  overlayLabel: {
    fontSize: 32,
    fontWeight: 'bold',
    textAlign: 'center',
  },
  overlayWrapper: {
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
  },
  emptyText: {
    fontSize: 18,
    color: '#666',
    marginBottom: 20,
  },
  reloadButton: {
    backgroundColor: '#FF6B6B',
    paddingHorizontal: 30,
    paddingVertical: 15,
    borderRadius: 25,
  },
  reloadButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
});