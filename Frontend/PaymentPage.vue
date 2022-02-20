<template>
  <div id="app" style="background-color:white">
    <br />
    <h1>Please enter the payment details for your workout</h1>
    <v-row align="center" justify="center">
      <v-col cols="8" sm="8">
        <p class="mt-7" v-if="publicPageBookingRecurring == false">
          YokD will charge your card a one time payment for your personal
          training session.<br />Your trainer will be notified, and you'll be
          able to chat with them immediately after.
        </p>
        <p class="mt-7" v-if="publicPageBookingRecurring">
          YokD will charge your card the total cost of each week at the start of each week, and your bookings will start the coming Monday. <br />
          Your Personal Trainer will be notified, and you'll be able to chat with them immediately after.
        </p>
        <div v-if="publicPageBookingRecurring==false">
          <h3 class="mt-9">Total: ${{ price }}</h3>
          <h3>Session Date: {{ sessionDate }}</h3>
          <h3>Location: {{ locationName }}</h3>
        </div>

        <div v-if="publicPageBookingRecurring">
          <h3 class="mt-9">Subscription Weekly Cost: ${{ price }}</h3>
          <h3>First Session Start Date: {{ firstSessionStartDate }} for {{numWeeks}} weeks.</h3>
          <h3>Weekdays Booked: {{weekdayShow}}</h3>
          <h3>Location: {{ locationName }}</h3>
        </div>
        <br /><br /><br />
        <v-row align="center" justify="center">
          <v-progress-circular
            color="red"
            indeterminate
            v-show="loading"
          ></v-progress-circular>
        </v-row>

        <v-row align="center" justify="center">
          <card
            class="stripe-card"
            id="card"
            :class="{ complete }"
            stripe="x"
            :options="stripeOptions"
            @change="complete = $event.complete"
          />
          <!--Test stripe key:x, 
           x-->
        </v-row>

        <small class="card-error">{{ error }}</small>
        <v-row align="center" justify="center">
          <v-btn
            color="red"
            class="pay-with-stripe ml-5 white--text"
            @click="pay"
            :disabled="!complete || loading"
          >
            Pay with card
          </v-btn>
        </v-row>
      </v-col>
    </v-row>
    <v-snackbar v-model="snackbar">
      {{ text }}

      <template v-slot:action="{ attrs }">
        <v-btn color="red" text v-bind="attrs" @click="snackbar = false">
          Close
        </v-btn>
      </template>
    </v-snackbar>
  </div>
</template>

<script>
import store from "../router/store";
import {
  Card,
  createPaymentMethod,
  confirmPaymentIntent,
} from "vue-stripe-elements-plus";
import axios from "axios";
import { yokdApiEndpoints } from "@/constants/apiEndpoints";
import moment from "moment";

export default {
  components: {
    Card,
  },
  mounted() {
    //store.commit('setPublicPageBooking',false);
    this.publicPageBookingRecurring = store.state.recurring;
    //this.stripeKey  = stripePromise;
    this.price = store.state.sessionPrice;
    this.locationName = store.state.sessionLocationName;
    this.sessionDate = store.state.sessionDate;
    this.numWeeks = store.state.recurringNumWeeks;

    var weekDays = "";
        for(var i=0;i<store.state.recurringBookings.length;i++){

        //Calculate start date:
        var slots = store.state.recurringBookings[i].split("|")
        if(slots != undefined){
          if (slots[0] == '0')
            weekDays += "Monday,";
          else if (slots[0] == '1')
            weekDays += "Tuesday,";
          else if (slots[0] == '2')
            weekDays += "Wednesday,";
          else if (slots[0] == '3')
            weekDays += "Thursday,";
          else if (slots[0] == '4')
            weekDays += "Friday,";
          else if (slots[0] == '5')
            weekDays += "Saturday,";
          else if (slots[0] == '6')
            weekDays += "Sunday,";
        }        
        this.weekdayShow = weekDays.slice(0,-1);
        this.firstSessionStartDate = moment(this.sessionStartDate).add(slots[0],'d').format("YYYY-MM-DD");
        this.firstSessionStartDate = new Date();
        if(new Date().getDay() == 1){
          this.firstSessionStartDate.setDate(this.firstSessionStartDate.getDate() + 7)
        }else{
          this.firstSessionStartDate.setDate(this.firstSessionStartDate.getDate() + (1 + 7 - this.firstSessionStartDate.getDay()) % 7);
        }
        this.firstSessionStartDate = moment(this.firstSessionStartDate).format("YYYY-MM-DD");
      }
  },
  data() {
    return {
      loading: false,
      complete: false,
      stripeKey: "",
      publicPageBookingRecurring: false,
      error: "",
      price: 0,
      locationName: "YokD HQ",
      sessionDate: new Date(),
      sessionStartDate:'',
      firstSessionStartDate:'',
      weekdayShow: '',
      clientSecret: "",
      numWeeks : 1,
      snackbar: false,
      text: "",
      stripeOptions: {
        // see https://stripe.com/docs/stripe.js#element-options for details
      },
      publishableKey: "x",
      publishableKeyTest:
        "x",
      token: null,
      charge: null,
      description: "YokD Fitness Training",
    };
  },
  methods: {
    submit() {
      this.$refs.elementsRef.submit();
    },
    convertToArmy(time,slot){
      //Assumes format of string 10:00
      var timeSplit = time.split(":");
      var hourValue = timeSplit[0];
      if(slot.includes("pm")){
        hourValue = parseInt(hourValue)+ 12;
      }
      return hourValue+":"+timeSplit[1];
    },
    postCalls(){
      confirmPaymentIntent(this.clientSecret)
        .then((response) => {
          //createABookingAndConversation
          
        })
        .catch(() => {
          this.loading = false;
          this.text =
            "There was an error processing this payment please try another!";
          this.snackbar = true;
        });
    },
    furtherPaymentCalls(response) {
      if (
        JSON.stringify(response.data).includes(
          "Invalid Token"
        )
      ) {
        this.loading = false;
        //handle duplicate
        this.text =
          "Invalid Token, please login again!";
        this.snackbar = true;
        store.commit('setToken','');
        store.commit('setIsLoggedIn',false);
        this.$cookie.set('setYokDToken', '', { expires: '10Y' });
        this.$cookie.set('setIsLoggedIn', false, { expires: '10Y' });
        this.$router.push('/signin');
        
      }
      if (response) {
        axios
          .get(
            yokdApiEndpoints.getTrainerAndClientStripeIDs
              .replace("REPLACETOKEN", store.state.token)
              .replace("REPLACETRAINERID", store.state.sessionTrainerAccountId)
          )
          .then((responseUserIds) => {
            var userIds = responseUserIds.data[0];
            if (userIds.stripeCustomerId) {

              if(store.state.publicPageBooking){
                if(store.state.recurring){
                  //Calculate next Monday, and add weeks then set start and end date.
                  var d = new Date();
                  if(new Date().getDay() == 1){
                    d.setDate(d.getDate() + 7)
                  }else{
                    d.setDate(d.getDate() + (1 + 7 - d.getDay()) % 7);
                  }
                  this.sessionStartDate = new Date(d);
                  axios.get(yokdApiEndpoints.createStripeRecurringPaymentReferralIntent
                      .replace(
                        "REPLACECUSTOMERSTRIPEID",
                        userIds.stripeCustomerId
                      )
                      .replace("REPLACETRAINERSTRIPEID", userIds.trainerStripeId)
                      .replace("REPLACESTARTTIME", Math.ceil(+d/1000))
                      .replace("REPLACEENDTIME", Math.ceil(+d.setDate(d.getDate() + store.state.recurringNumWeeks * 7)/1000))
                  )
                  .then((response) => {
                    this.clientSecret = response.data;
                    this.postCallsRecurring();
                  })
                  .catch((e) => {
                    console.log(e)
                    this.loading = false;
                    this.text =
                      "There was an error processing this payment please try another!";
                    this.snackbar = true;
                  });
                }else{
                  axios.get(yokdApiEndpoints.createStripePaymentIntentPublicPage
                    .replace(
                      "REPLACECUSTOMERSTRIPEID",
                      userIds.stripeCustomerId
                    )
                    .replace("REPLACETRAINERSTRIPEID", userIds.trainerStripeId)
                )
                .then((response) => {
                  this.clientSecret = response.data;
                  this.postCalls();
                })
                .catch(() => {
                  this.loading = false;
                  this.text =
                    "There was an error processing this payment please try another!";
                  this.snackbar = true;
                });
                }
              }else{
                if(store.state.recurring){
                  var dd = new Date();
                  if(new Date().getDay() == 1){
                    dd.setDate(dd.getDate() + 7)
                  }else{
                    dd.setDate(dd.getDate() + (1 + 7 - dd.getDay()) % 7);
                  }
                  this.sessionStartDate = new Date(dd);

                  axios.get(yokdApiEndpoints.createStripeRecurringPaymentReferralIntent
                      .replace(
                        "REPLACECUSTOMERSTRIPEID",
                        userIds.stripeCustomerId
                      )
                      .replace("REPLACETRAINERSTRIPEID", userIds.trainerStripeId)
                      .replace("REPLACESTARTTIME", Math.ceil(+d/1000))
                      .replace("REPLACEENDTIME", Math.ceil(+d.setDate(d.getDate() + store.state.recurringNumWeeks * 7)/1000))
                  )
                  .then((response) => {
                    this.clientSecret = response.data;
                    this.postCallsRecurring();
                  })
                  .catch((e) => {
                    console.log(e)
                    this.loading = false;
                    this.text =
                      "There was an error processing this payment please try another!";
                    this.snackbar = true;
                  });
                }
                else{
              axios.get(yokdApiEndpoints.createStripePaymentIntent
                    .replace(
                      "REPLACECUSTOMERSTRIPEID",
                      userIds.stripeCustomerId
                    )
                    .replace("REPLACETRAINERSTRIPEID", userIds.trainerStripeId)
                )
                .then((response) => {
                  this.clientSecret = response.data;
                  this.postCalls();
                })
                .catch(() => {
                  this.loading = false;
                  this.text =
                    "There was an error processing this payment please try another!";
                  this.snackbar = true;
                });
                }
              }
            } else {
              this.text =
                "There was an error with your card please try again or another!";
              this.snackbar = true;
            }
          })
          .catch((e) => {
            console.log(e)
            this.loading = false;
            this.text =
              "There was an error processing this payment please try another!";
            this.snackbar = true;
          });
      }
    },
    pay() {
      this.loading = true;
      //createToken().then(data => console.log(data.token))
      createPaymentMethod("card", {}).then((result) => {
        // Handle result.error or result.paymentMethod
        if (result.paymentMethod) {
          //Create customer with the newly created payment method
          axios
            .get(
              yokdApiEndpoints.attachStripeCardAndCreateCustomer
                .replace("REPLACETOKEN", store.state.token)
                .replace("REPLACEPAYMENTMETHODID", result.paymentMethod.id)
            )
            .then((response) => {
              this.furtherPaymentCalls(response);
            })
            .catch(function (error) {
              console.log("oops got an error." + error);
              this.text =
                "There was an error processing this payment please try another!";
              this.snackbar = true;
              this.loading = false;
            });
        } else {
          console.log(result.error);
          if (result.error.code == "card_declined") {
            this.text = "Your card was declined, please try another one.";
            this.snackbar = true;
          } else {
            this.text =
              "There was an error processing this payment please try another!";
            this.snackbar = true;
          }
          this.loading = false;
        }
      });
    },
  },
};
</script>

<style scoped>
.Header-logoImage {
  background-image: url("https://yokd.ca/wp-content/uploads/2019/09/Word-mark.png") !important;
}

#card {
  background-position: center;
}

.stripe-card {
  width: 70%;
  height: 140%;
  margin: 40px;
}
.stripe-card.complete {
  border-color: green;
}
</style>