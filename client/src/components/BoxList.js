import React, {Component} from "react";
import {Panel} from "react-bootstrap";
import Moment from "moment";
import PropTypes from 'prop-types';
import BoxOrdering from "./BoxOrdering";
import MyPagination from "./MyPagination";
import MySpinner from "./MySpinner";
import {Link} from "react-router";


class BoxList extends Component {
  renderBoxesList = () => {
    return this.props.boxes.map(box => {
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
    if (this.props.totalCount <= 10) {
      return null;
    }
    return (
        <MyPagination
            router={this.props.router}
            itemsCount={this.props.totalCount}
        />
    );
  };

  renderList = () => {
    if (this.props.totalCount === 0) {
      return <p className="text-center">No boxes</p>
    }

    if (!this.props.boxes.length) {
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
    return (
        <div>
          <BoxOrdering router={this.props.router} />
          {this.renderList()}
        </div>
    );
  }
}

BoxList.propTypes = {
  router: PropTypes.object.isRequired,
  boxes: PropTypes.array.isRequired,
  totalCount: PropTypes.number.isRequired,
};

export default BoxList;
