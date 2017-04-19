import React, {Component} from "react";
import {Panel} from "react-bootstrap";
import Moment from "moment";
import BoxOrdering from "./BoxOrdering";
import MyPagination from "./MyPagination";
import MySpinner from "./MySpinner";
import {Link} from "react-router";


export default class BoxList extends Component {
  renderBoxesList = () => {
    return this.boxTags.map(tag => {
      const box = this.props.boxes[tag];
      return (
          <Link
              to={`/boxes/${box.tag}`}
              key={box.tag}
          >
            <Panel>
              <div>
                <h4>
                  {box.tag}
                  {' | '}
                  <small>{box.pulls} pulls</small>
                </h4>
                <p>{box.short_description}</p>
              </div>
              <small title={Moment(box.date_updated).format('LLL')}>
                Last updated: {Moment(box.date_updated).fromNow()}
              </small>
            </Panel>
          </Link>
      );
    });
  };

  renderPagination = () => {
    if (this.boxPages.count <= 10) {
      return null;
    }
    return (
        <MyPagination
            router={this.props.router}
            itemsCount={this.boxPages.count}
        />
    );
  };

  renderList = () => {
    if (this.boxPages && this.boxPages.count === 0) {
      return <p className="text-center">No boxes</p>
    }

    if (!this.boxPages || !this.boxTags.length) {
      return <MySpinner />;
    }

    return (
        <div>
          <div className="box-list">
            {this.renderBoxesList()}
          </div>
          {this.renderPagination()}
        </div>
    )
  };

  render() {
    this.activePage = parseInt(this.props.router.location.query.page || 1, 10);
    this.boxPages = this.props.boxesPages;
    this.boxTags = (this.boxPages && this.boxPages.pages[this.activePage]) || [];
    return (
        <div>
          <BoxOrdering router={this.props.router} />
          {this.renderList()}
        </div>
    );
  }
}
