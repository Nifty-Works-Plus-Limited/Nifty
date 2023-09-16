from django.urls import path, include
from content import views
from users import views as usersViews
from payments import views as paymentViews
from rest_framework.urlpatterns import format_suffix_patterns

from content import views


urlpatterns = [

    # api version 1
    path('v1/', include([

        # Authentication
        path('nifty-auth/', include('auth_server.urls')),

        # users
        path('users', usersViews.UserList.as_view()),
        path('user/signup', usersViews.SignUpView.as_view()),
        path('user/signin', usersViews.SignInView.as_view()),
        path('user/signout', usersViews.SignOutView.as_view()),
        path('user/info', usersViews.UserInfo.as_view()),
        path('user/update-password', usersViews.UpdatePassword.as_view()),

        # payment
        path('payment', paymentViews.PaymentList.as_view()),
        path('payment/info', paymentViews.PaymentInfo.as_view()),
        path('pay', paymentViews.MakePayment.as_view()),
        path('pay/verify', paymentViews.VerifyPayment.as_view()),

        # subscription
        path('subscription/cancel', paymentViews.CancelSubscription.as_view()),

        # content paths
        # movies
        path('content/movies/', views.movieList.as_view(), name="movies"),
        path('content/movies/<slug>/', views.movieObject.as_view(), name="movie"),
        path('signedUrls/movieSignedUrl/', views.createMovieSignedUrl.as_view()),
        path('postContent/movies/', views.createMovieView.as_view()),
        path('postContent/movieMetaData/',
             views.createMovieMetaDataView.as_view()),
        path('search/movies/', views.MovieSearchView.as_view()),

        # podcasts
        path('content/podcasts/', views.PodcastObjectList.as_view(), name="podcasts"),
        path('content/podcasts/<slug>/',
             views.PodcastObject.as_view(), name="podcast"),
        path('signedUrls/podcastDetailSignedUrl/',
             views.createPodcastDetailSignedUrl.as_view()),
        path('postContent/podcastDetails/',
             views.createPodcastDetailView.as_view()),
        path('signedUrls/podcastEpisodeSignedUrl/',
             views.createPodcastEpisodeSignedUrl.as_view()),
        path('postContent/podcastEpisodes/',
             views.createPodcastEpisodesView.as_view()),
        path('postContent/podcastDetailMetaData/',
             views.createPodcastDetailMetaDataView.as_view()),

        # shows
        path('content/shows/', views.showDetailsList.as_view(), name="shows"),
        path('content/shows/<slug>/', views.showObject.as_view(), name="show"),
        path('signedUrls/showDetailSignedUrl/',
             views.createShowDetailSignedUrl.as_view()),
        path('postContent/showDetails/', views.createShowDetailView.as_view()),
        path('signedUrls/seasonDetailSignedUrl/',
             views.createSeasonDetailSignedUrl.as_view()),
        path('postContent/seasonDetails/',
             views.createseasonDetailView.as_view()),
        path('signedUrls/showEpisodeSignedUrl/',
             views.createShowEpisodeSignedUrl.as_view()),
        path('postContent/showEpisodes/', views.createshowEpisodeView.as_view()),
        path('postContent/showDetailMetaData/',
             views.createShowDetailMetaDataView.as_view()),

        # feeds
        path('postContent/RSSFeedUrl/', views.createRSSFeedUrlView.as_view()),
        path('updateContent/RSSFeedDetails/', views.updateFeeds.as_view()),

        path('categories/<str:contentTheme>/',
             views.ContentThemeView.as_view()),
        path('search/', views.SearchView.as_view()),



    ]))

]
