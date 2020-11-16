# ebuy (for lack of a better name)
## Introduction
An independent project to determine driving factors in Ebay selling prices for a personal favorite game of mine: "Super Smash Bros. Melee, 2001."  
The motivation here is to build a full-fledged, end-to-end Data Science project. This includes the data collection process, proper data storage, data exploration/visualization, data wrangling, and an informative model. Beyond this, Git version control and more standard software developer practices will be used in my pursuit to not be another hacky data monkey who can kind of code.
## 1. Data Collection
Aspiring data scientists and ML-practitioners get much of their training from sources like Kaggle. While this is a great resource, it is typically not indicative of real world data. Data from the world is ugly, brutish, and fragmented. To simulate this as best as possible, we go straight to the horse's mouth.

Raw. Data.

Luckily, the internet is chock-full of the stuff. My first attempt to start siphoning data off of Ebay was the more standard approach of working through an API. However, the Ebay API doesn't give you access to quite everything on an item listing. It *may* have been possible to acquire all of the info through complex API navigation, but the Ebay API docs are so mucky and inconsistent that I felt it more worthwhile to write a web-scraper that gives me full control over what data comes in to the system.

A quick ethical note: web scraping isn't exactly a nice thing to do. Aggressive querying of the same servers can cause performance issues for the company, and they may blacklist your IP if they identify you as a problem. Even if you circumvent this by using proxy services like I did, be kind and throttle your requests.

**Sample Smash Bros. Listing**
![Sample_listing.png](readme_images/Sample_listing.png)
We'll gather data from listings like the one above. For example, we'll pull the final selling price, the seller score, and the seller's feedback percentage. There are numerous other pieces of info that are retrieved, such as the seller's custom text description, but you get the gist. See the data_collection module for the details.

Besides the text-based data gathered above, it's noteworthy that the data_collection module also allows for downloading the item images, a core component of the modeling process.

All of this data is then fed into a local PostgreSQL database. This is done in a batching process across all of the available listings that have been sold and are not already in the database. Combining this with a CRON job on a UNIX system fully automates this portion of the pipeline.  Refer to the conf.yaml file to setup connection options for PostgreSQL (ports, etc.).

After all was said and done, I started analyzing data with approximately 1500 listings. This is a **small** dataset. Terribly small. However, this particular item does not sell that frequently, so at any given time there are only approximately 600 unique listings (already sold, mind you). After about 4 months of data collection, I began analyzing. I kept in mind that the root of my future problems would come from the size of the dataset.

## 2. Image Handling
The images. Oh, the images. There were approximately 6000 images to go alongside the PostgreSQL data. The images tell a lot about the item listed. For instance, they can tell you if the item includes all the expected components, (Game case, disc, manual). They can tell you if the listing isn't even the item you are after, thus providing a powerful filter before modeling. However, 6000 is far too small to get anything meaningful out of an unsupervised learning method to be helpful, and the features to be extracted are too helpful to be ignored.

So we resort to the only option. Manual labeling. I recommend never doing this if you want to retain sanity.

The data_collection/image_labeling.py script provides a kind interface to sift through the downloaded images and label relevant features. Below is a screenshot of the script in action.

**Image Feature Extraction**
![grueling_process.png](readme_images/grueling_process.png)

The features extracted from the images included Correct Disc, Backside of Disc, Correct Case, Correct Manual, Television Screenshot, Multiple Discs, and Multiple Cases. The last two features are useful in filtering out *bundled items*, listings where the seller is combining many games as one item. We want to limit our working dataset to only Super Smash Bros Melee listings.

## 3. Text Processing
The top two telling components of a listing are the images and the seller's text description. Naturally, we want to dissect the latter piece via NLP techniques. Again, given the small size of the dataset, we can't delve into anything *too* sophisticated.

We'll clean up the text and make it more uniform:

1. Remove punctuation
2. Remove stop words like 'a' or 'that'
3. Lemmatize each word: 'ran' -> 'run'

With all the text cleaned up, we then focus in on the words that show up enough to be worth calling  a feature, but not so frequently that it doesn't tell us anything about the listing. The specific criterion I selected was words, specifically 2-gram word combinations, with a **document frequency** in the range [0.02, 0.65]. This produced approximately 250 unique word features, which were then filled with counts of each word on a per-listing basis.

## 4. Data Visualization
Before any sort of modeling occurs, it is necessary to become more acquainted with the data at hand. Relevant visuals such as response (selling price) distribution, how response varies with particular features, and checks for multicollinearity are all captured in one, clean dashboard utilizing Streamlit. The more and more I use Streamlit, the more fond of it I become. See below for a sample screenshot.

 ![streamlit_sample.png](readme_images/streamlit_sample.png)
 
 Above, you see the response distribution in a simple matplotlib style. Had the dashboard been the main focus of this project, a more visually appealing package like seaborn or plotly could have been used, but since I'm only interested in a few basic exploratory questions, it's fine as is. A particularly useful feature of Streamlit, however, is it's ability to incorporate filters. For instance, above I am able to tie in an image-based filter that catches most of the non-"Super Smash Bros. Melee" items. Useful!
## 5. Final Data Prep
There are still a few more tidying steps required before we can get to the models.

First, we filter out items that have images that meet either of the below conditions.
* None of the images contain the correct case, correct disc, or correct manual.
* Any of the images contain multiple discs or multiple cases.

This helps ensure our dataset consists only of the specific item we want. Otherwise there will be added variance to the selling price for features beyond the scope of our initial question.

Second, we join in both the NLP Bag-of-Words-like features and the image features  to the main dataset. A few left-joins here does the trick.

Lastly, we need to account for missing values. As with all real world data, there were missing values galore. Each column was handled on a case-by-case basis. Some columns made the most sense for a simple mean or median imputation, some had such scarce NaNs that it was appropriate to drop a few rows, while other times it made sense to create the new category of "Missing". See modeling/data_handling_notes.txt for the details.
## 6. Modeling
It is worth restating the goal of this project. It is not to produce the best predictive model for new items. The goal is to determine which factors within a listing drive its selling price. This means that we must have some sense of interpretability to go alongside the model. That being said, we must bid farewell to any hopes of Neural Nets (we don't have nearly enough data for this anyways) or Random Forests.

So what are we left with as options? Moving from least interpretable to most, a selection of options includes Support Vector Regression, Decision Trees (Gradient Boosting is an option depending on *how* interpretable we want to get), or something more vanilla like a penalized linear regression.